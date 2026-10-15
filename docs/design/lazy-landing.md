# Thiết kế: Lười Code Studio — "Quán cóc đầu ngõ"

Chốt ngày 2026-10-16. Phiên leader đề xuất 3 hướng theo quy trình skill `frontend-design`, leader chọn hướng 2. Hai hướng còn lại ghi ở cuối để tham khảo. File này là nguồn sự thật cho R6–R13: token, font, bố cục và nguyên tắc lấy từ đây.

Hướng đã chọn: 2 — Quán cóc đầu ngõ

Leader duyệt:

## Ngữ cảnh
- **Chủ đề:** dịch vụ làm website của một vibe coder lười, giọng tự giễu; tiếng Việt (bản Anh ở R13).
- **Người xem:** chủ shop nhỏ, quán ăn, người làm tự do, cần một trang web mà không muốn tự làm.
- **Việc chính của trang:** khiến người xem bấm "Gửi thư cho tôi" (`mailto:hello@example.com`).
- **Ý tưởng:** quán cóc đầu ngõ. Dịch vụ được bày như bảng menu sơn tay của quán vỉa hè: ghế nhựa xanh đỏ, tường vôi, ly trà đá. Gọi món là thuê làm web.

## Bảng màu

### Sáng
| Tên | Hex | Vai trò |
|---|---|---|
| Tường vôi | `#F2F5F0` | nền trang (ngả xanh vôi, không phải kem) |
| Mực bảng | `#22313F` | chữ thân bài, viền bảng menu, nét vẽ SVG |
| Ghế nhựa xanh | `#2B6CB0` | link, tiêu đề phụ, ghế xanh trong SVG |
| Ghế nhựa đỏ | `#C42F2F` | **điểm nhấn**: giá trong menu, nút hành động (chữ trắng trên đỏ), ghế đỏ |
| Trà đá | `#F4B942` | mảng trang trí: ly trà, gạch chân bảng hiệu, nền số thứ tự gọi món (chữ Mực bảng trên nền này) |
| Bụi đường | `#5B6B7A` | chữ phụ (footer, chú thích) |

Tương phản đã tính (WCAG, phiên leader 2026-10-16):

| Cặp | Tỉ lệ |
|---|---|
| Mực bảng / Tường vôi | 12,1 |
| trắng / Ghế nhựa xanh | 5,4 |
| trắng / Ghế nhựa đỏ | 5,5 |
| Ghế nhựa đỏ / Tường vôi | 5,0 |
| Ghế nhựa xanh / Tường vôi | 4,9 |
| Mực bảng / Trà đá | 7,5 |
| Bụi đường / Tường vôi | 5,0 |

Không dùng `#D93A3A`: đỏ đó trên Tường vôi chỉ đạt 4,1.

### Tối ("Hẻm lúc lên đèn")
| Tên | Hex | Vai trò |
|---|---|---|
| Hẻm đêm | `#1B2A3A` | nền (xanh đá, không gần đen) |
| Đèn đường | `#E8EEF2` | chữ thân bài, nét vẽ SVG |
| Ghế xanh đêm | `#7FB2FF` | link, tiêu đề phụ |
| Ghế đỏ đêm | `#FF7A6E` | điểm nhấn: giá, nút (chữ Hẻm đêm trên nền này) |
| Trà đá | `#F4B942` | giữ nguyên; chữ Hẻm đêm trên nền này |
| Khói | `#9FB0BF` | chữ phụ |

Tương phản đã tính:

| Cặp | Tỉ lệ |
|---|---|
| Đèn đường / Hẻm đêm | 12,5 |
| Ghế đỏ đêm / Hẻm đêm | 5,7 |
| Ghế xanh đêm / Hẻm đêm | 6,8 |
| Hẻm đêm / Trà đá | 8,3 |
| Khói / Hẻm đêm | 6,6 |

## Kiểu chữ
- **Baloo 2** (Google Fonts, có subset `vietnamese`), độ đậm 700 và 800: bảng hiệu, `<h1>`, `<h2>`, tên món trong menu. Chữ tròn, dày, như chữ sơn tay trên bảng hiệu quán.
- **Be Vietnam Pro** (Google Fonts, `vietnamese`), độ đậm 400 và 600: thân bài, nút, FAQ.
- Hai họ font khác rõ (tròn dày / grotesk gọn). Font dự phòng: `"Baloo 2", "Arial Rounded MT Bold", system-ui, sans-serif` và `"Be Vietnam Pro", system-ui, sans-serif`.
- **Thang cỡ chữ** (tỉ lệ 1,25, gốc 18px), dùng `clamp()` cho h1 và h2:

| Thẻ | 360 | 1280 |
|---|---|---|
| `<h1>` | 40px | 64px |
| `<h2>` | 28px | 40px |
| tên món | 22px | 26px |
| thân bài | 18px | 18px |
| chữ phụ | 15px | 15px |

- Thân bài `line-height: 1,6`, dòng ≤ 65 ký tự.
- **Bảng hiệu:** dòng "Lười Code Studio" ở header là chữ sơn của chính bảng hiệu, viết hoa bằng nội dung chứ không bằng `text-transform`. Đây là chất liệu của chủ đề, không phải nhãn VIẾT HOA trên mỗi tiêu đề.

## Bố cục

### Nguyên tắc
- Căn trái trong một khung `max-width: 72rem`.
- Hero chia hai cột ở 1280 (chữ trái, minh hoạ phải), một cột ở 360.
- Menu dịch vụ là **một bảng duy nhất** có viền Mực bảng dày 3px, bo góc nhỏ 6px như tấm bảng gỗ. Không phải 3 thẻ rời giống nhau.
- **Thứ tự các phần:** header (bảng hiệu + nút) → hero → menu (`#dich-vu`) → gọi món (`#cach-lam`) → (R12: `#du-an`, `#hoi-dap`) → liên hệ (`#lien-he`) → footer.

### 1280
```
┌──────────────────────────────────────────────────────────────────────────┐
│ LƯỜI CODE STUDIO  ▔▔▔(gạch trà đá)                       [Gửi thư cho tôi]│
├──────────────────────────────────────────────────────────────────────────┤
│ Làm web cho bạn.                         │      (SVG: 2 ghế nhựa xanh/đỏ,  │
│ Ngồi xuống uống ly trà đá đã.            │       ly trà đá, laptop đang   │
│ Bạn kể, AI viết, tôi bấm deploy.         │       "tự code", người ngủ gật)│
│ [Gửi thư cho tôi]                        │                                │
├──────────────────────────────────────────────────────────────────────────┤
│ Menu hôm nay                                                             │
│ ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓  │
│ ┃ (ly)  Gói Cà Phê ............................. 1 ly + 1 câu prompt ┃  │
│ ┃       Trang giới thiệu một trang, gọn gàng.                         ┃  │
│ ┃ (ly)  Gói Trà Sữa .......................... 2 ly + 1 buổi kể khổ  ┃  │
│ ┃ (nồi) Gói Bao Cả Bữa ........................ 1 bữa lẩu + 3 lần sửa ┃  │
│ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛  │
├──────────────────────────────────────────────────────────────────────────┤
│ Gọi món thế nào   (1) Bạn kể   (2) AI viết, tôi đọc lại   (3) Tôi deploy │
│                   số trong hình tròn Trà đá, như số thứ tự gọi món        │
├──────────────────────────────────────────────────────────────────────────┤
│ Liên hệ: một câu + [Gửi thư cho tôi]           (SVG nhỏ: ghế trống chờ)  │
└──────────────────────────────────────────────────────────────────────────┘
```

### 360
```
┌────────────────────────────┐
│ LƯỜI CODE STUDIO  [Gửi thư]│
│ Làm web cho bạn.           │
│ Ngồi xuống uống ly đã.     │
│ [Gửi thư cho tôi]          │
│ (SVG ghế + ly, rộng 100%)  │
│ Menu hôm nay               │
│ ┏━━━━━━━━━━━━━━━━━━━━━━━━┓ │
│ ┃(ly) Gói Cà Phê         ┃ │
│ ┃ ......... 1 ly + prompt┃ │  ← giá xuống dòng, dấu chấm dẫn co lại
│ ┃(ly) Gói Trà Sữa        ┃ │
│ ┗━━━━━━━━━━━━━━━━━━━━━━━━┛ │
│ (1) Bạn kể                 │
│ (2) AI viết                │
│ (3) Tôi deploy             │
│ Liên hệ + [Gửi thư cho tôi]│
└────────────────────────────┘
```

## Nguyên tắc
1. **Điểm nhấn duy nhất là bảng menu.** Dấu chấm dẫn giữa tên món và giá (CSS `border-bottom: dotted` hoặc `::after` với `leader`), giá màu Ghế nhựa đỏ. Mọi phần khác tiết chế.
2. **Đồ vật của quán là đồ hoạ:** ghế nhựa đẩu (xanh, đỏ), ly trà đá có đá viên, nồi lẩu, laptop. SVG nét Mực bảng 2,5px, tô màu phẳng, không gradient, không bóng.
3. **Ngôn ngữ của quán cho nội dung:**
   - "Menu hôm nay", "Gọi món thế nào", "Ghé quán" (thay cho "Liên hệ" trong tiêu đề hiển thị; id vẫn `lien-he`);
   - nút "Gửi thư cho tôi";
   - không chữ đệm.
4. **Số thứ tự chỉ ở "Gọi món thế nào"**, vì đó là chuỗi bước thật.
5. **Chuyển động (R7):**
   - một khoảnh khắc lúc tải trang: hai cái ghế "được kéo ra" và hơi nước bốc từ ly;
   - tương tác: nút "Để tôi lười giúp bạn" làm người trong minh hoạ ngáp và laptop hiện dòng "deploying…".
6. **Bỏ bớt một món phụ kiện:** không thêm hoạ tiết nền, không dải gradient, không icon trang trí ngoài các đồ vật của quán.

## Dấu hiệu AI đã tránh
1. **Nền kem + serif + đất nung:** nền Tường vôi `#F2F5F0` ngả xanh vôi; không serif; đỏ là đỏ ghế nhựa `#C42F2F`, không phải đất nung `#D97757`.
2. **Nền gần đen + accent axit:** chế độ tối dùng xanh đá `#1B2A3A` với hai màu ghế, không có xanh axit.
3. **Bố cục báo giấy:** không đường kẻ mảnh, không cột dày; một viền dày bo góc nhỏ cho tấm bảng.
4. **Bộ thẻ SaaS:** dịch vụ là một bảng menu liền, không phải 3 thẻ giống nhau; không bóng `rgba(0,0,0,.1)`; không gradient.
5. **Khung mẫu:** không nhãn VIẾT HOA giãn chữ trên tiêu đề (chỉ bảng hiệu là chữ sơn); không chuỗi `A · B · C`; không nhãn "CHỮ — mảnh"; màu chữ là Mực bảng `#22313F`, không phải `#111`; không font mono; không `→` sau link.

**Tự phê bình:** đề "landing page cho freelancer làm web" thường ra một hero gradient với 3 thẻ giá. Hướng này lấy riêng chất liệu quán cóc Việt và cách gọi món, nên khó ra trùng. Nếu thấy giống trang khác, bỏ trước tiên mọi thứ không thuộc quán.

## Hai hướng không chọn (tham khảo)
- **Hướng 1 — Giờ ngủ trưa:** Lá chuối `#2F6B4F`, Nắng trưa `#F6D365`, Võng hồng `#E86A92`, Gió mát `#EEF5F1`, Mực `#1E2A38`; Pangolin + Be Vietnam Pro; tiêu đề hero võng xuống như cái võng.
- **Hướng 3 — Tin nhắn lúc 2 giờ sáng:** `#4A5BDC`, `#E9ECF5`, `#8E6CEF`, `#FBFBFE`, `#1F2333`; Lexend; cả trang là một cuộc chat, hero có "đang gõ…".
