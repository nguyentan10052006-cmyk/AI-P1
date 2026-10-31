-- filter.lua: chuyển Markdown của docs/report sang LaTeX cho khung báo cáo.
-- 1. Đoạn "**Bảng x.y.** ..." ngay trước một bảng thành chú thích của bảng đó,
--    để chú thích không bị tách khỏi bảng khi sang trang.
-- 2. Đoạn chỉ có một hình, kèm đoạn "*Hình x.y. ...*" ngay sau, thành một figure có chú thích.
-- 3. Độ rộng cột tính theo độ dài chữ trong cột, thay vì chia đều; tiêu đề cột in đậm.

local stringify = pandoc.utils.stringify

local function ulen(s)
  return utf8.len(s) or #s
end

-- Số ký tự trên một dòng của bảng (cỡ chữ \small, trang dọc); trang ngang truyền TABLE_LINE lớn hơn.
local LINE = tonumber(os.getenv("TABLE_LINE") or "") or 72

local function is_table_caption(b)
  return b and b.t == "Para" and #b.content >= 1 and b.content[1].t == "Strong"
    and stringify(b.content[1]):match("^Bảng") ~= nil
end

local function is_image_para(b)
  return b and b.t == "Para" and #b.content == 1 and b.content[1].t == "Image"
end

local function is_figure_caption(b)
  return b and b.t == "Para" and #b.content >= 1 and b.content[1].t == "Emph"
    and stringify(b.content[1]):match("^Hình") ~= nil
end

local function column_stats(tbl)
  -- maxlen: chữ dài nhất trong thân bảng (tiêu đề được phép xuống dòng);
  -- head: chữ dài nhất của tiêu đề; maxword: từ dài nhất (cả tiêu đề), không được ngắt.
  local ncols = #tbl.colspecs
  local maxlen, head, maxword = {}, {}, {}
  for j = 1, ncols do maxlen[j] = 1; head[j] = 1; maxword[j] = 1 end
  local function visit(row, into)
    local j = 1
    for _, cell in ipairs(row.cells) do
      local s = stringify(cell.contents)
      if ulen(s) > into[j] then into[j] = ulen(s) end
      for w in s:gmatch("%S+") do
        if ulen(w) > maxword[j] then maxword[j] = ulen(w) end
      end
      j = j + (cell.col_span or 1)
    end
  end
  for _, row in ipairs(tbl.head.rows) do visit(row, head) end
  for _, body in ipairs(tbl.bodies) do
    for _, row in ipairs(body.body) do visit(row, maxlen) end
  end
  return ncols, maxlen, head, maxword
end

local function set_widths(tbl)
  local ncols, maxlen, head, maxword = column_stats(tbl)
  local natural = 0
  for j = 1, ncols do natural = natural + math.max(maxlen[j], head[j]) + 2 end
  if natural <= LINE then
    for j = 1, ncols do tbl.colspecs[j] = {tbl.colspecs[j][1], nil} end
    return
  end
  -- Mỗi cột có sàn (từ dài nhất không bị ngắt; tiêu đề tối đa khoảng 2 dòng) và độ rộng mong muốn
  -- (đủ cho chữ dài nhất trên một dòng). Tìm ngưỡng T: cột nào muốn rộng hơn T thì chỉ được T,
  -- nên cột ngắn giữ đủ chỗ còn các cột dài chia đều phần còn lại.
  local floor1, floor2, desired = {}, {}, {}
  local s1, s2 = 0, 0
  for j = 1, ncols do
    floor1[j] = math.min(maxword[j], 16) + 2
    floor2[j] = math.max(floor1[j], math.min(math.ceil(head[j] * 0.55), 20) + 2)
    desired[j] = math.max(maxlen[j] + 2, floor2[j])
    s1 = s1 + floor1[j]
    s2 = s2 + floor2[j]
  end
  local fl = (s2 <= LINE) and floor2 or floor1
  local function width_at(t)
    local sum = 0
    for j = 1, ncols do sum = sum + math.max(fl[j], math.min(desired[j], t)) end
    return sum
  end
  local lo, hi = 0, 0
  for j = 1, ncols do hi = math.max(hi, desired[j]) end
  for _ = 1, 50 do
    local mid = (lo + hi) / 2
    if width_at(mid) > LINE then hi = mid else lo = mid end
  end
  local w, total = {}, 0
  for j = 1, ncols do
    w[j] = math.max(fl[j], math.min(desired[j], lo))
    total = total + w[j]
  end
  total = math.max(total, LINE)
  local caps = {}
  for j = 1, ncols do
    tbl.colspecs[j] = {tbl.colspecs[j][1], w[j] / total}
    caps[j] = w[j] / total * LINE - 2
  end
  return caps
end

-- Bảng có ô xuống dòng thì kẻ ngang mảnh giữa các hàng cho dễ đọc; bảng mỗi hàng một dòng thì không.
local function wraps(tbl, caps)
  for _, body in ipairs(tbl.bodies) do
    for _, row in ipairs(body.body) do
      local j = 1
      for _, cell in ipairs(row.cells) do
        if #cell.contents > 1 then return true end
        local s = stringify(cell.contents)
        if s:find("\n") then return true end
        if caps and ulen(s) > caps[j] + 0.5 then return true end
        j = j + (cell.col_span or 1)
      end
    end
  end
  return false
end

local function bold_header(tbl)
  for _, row in ipairs(tbl.head.rows) do
    for _, cell in ipairs(row.cells) do
      cell.contents = cell.contents:walk({
        Plain = function(p) return pandoc.Plain({pandoc.Strong(p.content)}) end
      })
    end
  end
end

function Table(tbl)
  local caps = set_widths(tbl)
  bold_header(tbl)
  if wraps(tbl, caps) then
    return {pandoc.RawBlock("latex", "%ROWRULES"), tbl}
  end
  return tbl
end

function Blocks(blocks)
  local out = pandoc.Blocks({})
  local i = 1
  while i <= #blocks do
    local b, nb = blocks[i], blocks[i + 1]
    if is_table_caption(b) and nb and nb.t == "Table" then
      nb.caption = {long = pandoc.Blocks({pandoc.Plain(b.content)})}
      out:insert(nb)
      i = i + 2
    elseif is_image_para(b) then
      local img = b.content[1]
      if not img.attributes.width then img.attributes.width = "86%" end
      local cap = pandoc.Blocks({})
      if is_figure_caption(nb) then
        cap = pandoc.Blocks({pandoc.Plain(nb.content[1].content)})
        i = i + 2
      else
        i = i + 1
      end
      out:insert(pandoc.Figure(pandoc.Blocks({pandoc.Plain({img})}), {long = cap}))
    else
      out:insert(b)
      i = i + 1
    end
  end
  return out
end

-- Mã trong dòng: cho phép xuống dòng sau / _ . - để tên tệp dài không tràn lề
local TEX = {["\\"] = "\\textbackslash{}", ["{"] = "\\{", ["}"] = "\\}", ["#"] = "\\#", ["$"] = "\\$",
  ["%"] = "\\%", ["&"] = "\\&", ["~"] = "\\textasciitilde{}", ["^"] = "\\textasciicircum{}",
  ["_"] = "\\_\\allowbreak{}", ["/"] = "/\\allowbreak{}", ["."] = ".\\allowbreak{}", ["-"] = "-\\allowbreak{}"}
function Code(c)
  local body = c.text:gsub("[\\{}#$%%&~^_/%.%-]", TEX)
  return pandoc.RawInline("latex", "\\texttt{" .. body .. "}")
end

-- [chữ]{.dien}: chỗ còn phải điền, hiện chữ đỏ nghiêng trong PDF
function Span(sp)
  if sp.classes:includes("dien") then
    local out = pandoc.Inlines({pandoc.RawInline("latex", "\\placeholder{")})
    out:extend(sp.content)
    out:insert(pandoc.RawInline("latex", "}"))
    return out
  end
end

-- URL viết trần trong văn bản thành liên kết (\\url ngắt dòng được ở mọi chỗ)
-- h_P, h_M viết thường trong văn bản thành ký hiệu toán $h_P$, $h_M$ như ở các chương khác
function Str(el)
  local url, tail = el.text:match("^(https?://.-)([%.,;:%)]*)$")
  if url then
    local out = pandoc.Inlines({pandoc.Link(url, url)})
    if tail ~= "" then out:insert(pandoc.Str(tail)) end
    return out
  end
  if el.text:find("h_[PM]") then
    local out, pos = pandoc.Inlines({}), 1
    while true do
      local a, b, which = el.text:find("h_([PM])", pos)
      if not a then break end
      if a > pos then out:insert(pandoc.Str(el.text:sub(pos, a - 1))) end
      out:insert(pandoc.Math("InlineMath", "h_" .. which))
      pos = b + 1
    end
    if pos <= #el.text then out:insert(pandoc.Str(el.text:sub(pos))) end
    return out
  end
end

-- Thứ tự: gắn chú thích (Blocks), rồi tính độ rộng cột (Table) khi mã trong dòng còn là Code,
-- cuối cùng mới đổi Code, Span, URL sang LaTeX.
return {
  {Blocks = Blocks},
  {Table = Table},
  {Span = Span, Code = Code, Str = Str},
}
