import qrcode
from PIL import Image, ImageDraw, ImageFont
import time

# Function to create the QR code
def create_qr_code(data, box_size=160, border=4):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=box_size // 11,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img = img.resize((box_size, box_size))

    return img

# Get user input for userID and userName
user_id = input("Enter userID: ")
user_name = input("Enter userName: ")

# Format the data as "userID|userName"
data = f"{user_id}|{user_name}"

# Create the main canvas with a 2-pixel border
main_img = Image.new("RGB", (204, 254), "white")
border_color = "black"  # Color of the border

# Create a border around the entire canvas
draw = ImageDraw.Draw(main_img)
draw.rectangle([(0, 0), (203, 253)], outline=border_color, width=2)

# Create the QR code image
qr_code = create_qr_code(data, box_size=200, border=4)
# Position the QR code centered inside the border
position = ((204 - qr_code.size[0]) // 2, 4)
main_img.paste(qr_code, position)

# Draw the dividing line
draw.line([(0, 202), (202, 202)], fill=border_color, width=2)

# Calculate the maximum available width for the text
text_max_width = 160

# Load a sans-serif font without antialiasing
font_size = 24
font = ImageFont.truetype("arial.ttf", font_size)  # Replace "arial.ttf" with the path to your desired font file
text = f"{user_name}"

# Dynamically adjust the font size to fit the available width
while font.getsize(text)[0] > text_max_width:
    font_size -= 1
    font = ImageFont.truetype("arial.ttf", font_size)

# Calculate the position to center the text horizontally
text_x = 20 + (text_max_width - font.getsize(text)[0]) // 2

# Calculate the position to center the text vertically
text_y = 212  # Positioned at the bottom with 2-pixel offset

# Draw the user name text with the adjusted font size
draw.text((text_x, text_y), text, fill="black", font=font)

# Generate a timestamp
timestamp = time.strftime("%Y%m%d%H%M%S")

# Save the final image with a filename based on the employee's name and timestamp
file_name = f"{user_name}_{timestamp}.png"
main_img.save(file_name)

print(f"QR code saved as {file_name}")
