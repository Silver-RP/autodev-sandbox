# Mục tiêu: landing page "vibe coder lười" (`lazy-landing`)

Bản 2 (2026-10-16): sửa mục tiêu sau R3. Bản 1 (tối giản) ở lịch sử git (PR #12).

## Mục tiêu
Landing page cho dịch vụ làm website của một vibe coder lười biếng. Trang phải đẹp, có cá tính, không chỉ có chữ, và đi tới mức sản phẩm thật: SEO, hiệu năng, song ngữ, triển khai.

## Kết quả mong muốn (nguyên văn leader)
> Xây dựng website đơn giản, tối giản, 1 landing page về trang dịch vụ xây dựng trang web của 1 vibe coding lười biếng

Sau khi xem bản R3:
> haha, xấu quá, chỉ có text thôi. có thư viện hoặc có skill nào để agent có thể tự sáng tạo UI cho đẹp hơn không?

> sửa mục tiêu lazy-landing: landing page phải đẹp, có cá tính (dùng skill frontend-design), không chỉ có chữ; agent tự chụp màn hình để kiểm

> mở rộng raodmap hơn nữa, cụ thể hơn, chi tiết hơn và rộng hơn

## Cách hiểu đã chốt
- **Phần giữ từ bản 1:**
  - trang nằm ở `site/` trong repo sandbox, tiếng Việt;
  - tên hư cấu "Lười Code Studio", email giữ chỗ `hello@example.com`, giá dạng chữ đùa;
  - R3 (cấu trúc 4 phần, test, smoke HTTP) giữ nguyên.
- **Thiết kế** theo skill `frontend-design` (plugin `frontend-design@claude-plugins-official`, đã cài ở phạm vi user):
  - plan thiết kế gồm 4–6 màu hex, kiểu chữ, wireframe ASCII, nguyên tắc;
  - tự đối chiếu với 5 nhóm "dấu hiệu trang AI" của skill;
  - một điểm nhấn táo bạo, phần còn lại tiết chế.
- **Leader chọn hướng:** agent đưa 3 hướng kèm bản phác và ảnh, rồi dừng; leader chọn một hướng rồi agent mới dựng trang.
- **Agent tự nhìn trang:**
  - Chrome headless chụp 360px và 1280px, mỗi cỡ sáng và tối;
  - 360px phải chụp qua iframe, vì Chrome headless không thu khung nhìn dưới 500px (đã đo 2026-10-16);
  - chế độ tối giả lập bằng `--blink-settings=preferredColorScheme=0`;
  - reviewer đọc ảnh PNG.
- **Không chỉ chữ:** minh hoạ SVG inline tự vẽ cho hero, biểu tượng SVG cho các gói và các bước.
- **Tài nguyên ngoài:**
  - cho phép Google Fonts (`fonts.googleapis.com`, `fonts.gstatic.com`);
  - cho phép thư viện JS qua `cdn.jsdelivr.net` / `cdnjs.cloudflare.com`, ghim phiên bản, có `integrity` + `crossorigin`;
  - mọi domain khác vẫn cấm;
  - nội dung vẫn đủ khi tắt JS hoặc CDN lỗi.
- **Không có trần chi phí.** Ước tính theo số đo; báo nếu thực tế lệch quá 2 lần.
- **Phạm vi:** lõi R4–R8 (công cụ, hướng thiết kế, dựng trang, chuyển động, chế độ tối và truy cập) cộng mở rộng R9–R13 (SEO, hiệu năng, triển khai, nội dung, song ngữ).

## Nhật ký hỏi đáp
### Bản 1 (2026-10-16, PR #12)
| # | Câu hỏi | Trả lời |
|---|---|---|
| 1 | Trang đặt ở đâu? | 1: `site/` trong sandbox |
| 2 | Ngôn ngữ? | 1: tiếng Việt |
| 3 | Tên, email, giá? | 1: hư cấu, giữ chỗ, chữ đùa |
| 4 | Giới hạn chi phí? | 1: ≤ 5 USD |
| 5 | Hướng ROADMAP? | 1: R3 → R4 lát dọc |
| 6–9 | Duyệt tiêu chí, mốc, pre-mortem, thứ tự cắt | 1 cả bốn |

### Giữa bản 1 và bản 2
| Câu hỏi | Trả lời |
|---|---|
| Làm đẹp bằng cách nào? | "3,1": cài plugin `frontend-design` (đã kiểm nguồn Anthropic), rồi sửa mục tiêu, có design brief và chụp màn hình |
| PR #14 (R3)? | 1: merge làm nền |

### Bản 2
| # | Câu hỏi | Trả lời |
|---|---|---|
| 1 | Font lấy từ đâu khi vẫn giữ luật không tài nguyên ngoài? | 3: cho phép Google Fonts |
| 2 | Leader chọn hướng thiết kế trước khi code? | 1: có, 3 hướng, dừng chờ chọn |
| 3 | Cho phép JavaScript? | 3: thư viện qua CDN |
| 4 | Giới hạn chi phí? | 3: không giới hạn |
| 5 | Hướng ROADMAP | leader: "mở rộng roadmap hơn nữa, cụ thể hơn, chi tiết hơn và rộng hơn" |
| 5b | Lấy lớp mở rộng nào? | 7: tất cả (R9–R13) |
| 6 | Duyệt tiêu chí | 1 |
| 7 | Duyệt danh sách mốc | 1 |
| 8 | Duyệt pre-mortem | 1 |
| 9 | Duyệt thứ tự cắt, phần không cắt, việc chỉ người làm | 1 |

## Giả định còn lại
- **Ước tính:** USD = số task × 0,25 × hệ số + 0,75 supervisor, theo R1/R2 của sandbox.
  - Hệ số ×2 (mốc chụp và đọc ảnh) và ×1,5 (song ngữ) là giả định, chưa có số đo; đối chiếu sau R5.
  - USD của R3 chưa đo.
- **CDN và SRI:** chỉ `cdn.jsdelivr.net` hoặc `cdnjs.cloudflare.com`; thư viện chuyển động dự kiến là GSAP. P11 hoặc developer chọn phiên bản cụ thể.
- **Test cần Chrome hoặc mạng** (D1, D3–D6, SRI) tự `skip` khi máy không có Chrome hoặc mạng. CI chỉ chạy ruff + pytest, nên các test này có thể bị skip trên CI. Cổng thật là `verify.py` trên máy local và reviewer.
- **E2 (Lighthouse)** chạy local bằng `npx -y lighthouse@12` (Node v22 có sẵn), không chạy trong CI.
- **E3 (Pages):** repo private, cần leader bật Pages (gói trả phí hoặc đổi sang public). Chưa có thì R11 BLOCKED.
- **R5 dừng giữa chuỗi mốc:** chế độ A không có "chờ người" giữa mốc. Điểm dừng là kết thúc R5; R6 chỉ chạy khi dòng `Hướng đã chọn:` đã được điền.
- **Ba dự án hư cấu ở R12** đều ghi "ví dụ"; không có đánh giá khách hàng giả.
