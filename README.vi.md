# AI Video Edit Recipes (tiếng Việt)

Bộ video ngắn do AI (Claude Code) edit. Mỗi video kèm câu lệnh đã dùng, bạn cần đưa cho AI cái gì, công cụ nào, tốn bao nhiêu, và với phần lớn video là cả dự án để sửa lại.

**[Mở trang xem video](index.html)** · **[Xem intro 2 phút](intro/)** · [English](README.md)

## Tự làm một video

1. Cài [Claude Code](https://claude.com/claude-code), [Node.js 22+](https://nodejs.org) và [ffmpeg](https://ffmpeg.org).
2. Mở thư mục chứa video hoặc ảnh của bạn trong Claude Code.
3. Dán câu lệnh của video bạn thích, đổi tên, chữ, độ dài cho đúng của bạn.
4. AI dựng dự án HyperFrames, tự chụp khung hình để kiểm tra, rồi xuất MP4.

Muốn render lại một dự án có sẵn: chép `recipes/<id>/source/`, thêm các file trong `MEDIA.md`, rồi chạy `npx hyperframes render`.

## Chi phí

Phần lớn video **miễn phí** ngoài gói Claude: HyperFrames, ffmpeg, OpenCV, rembg, faster-whisper, librosa chạy trên máy; footage lấy từ Pexels. Chỉ các video ghi "credits" mới tốn tiền (HeyGen, Vbee hoặc giọng đọc AI khác).

## Ghi nguồn

Footage từ các tác giả trên Pexels (không phân phối lại trong repo). Tên thương hiệu trong video là hư cấu. Code và câu lệnh: MIT.
