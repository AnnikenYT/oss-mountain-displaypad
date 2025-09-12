from PIL import Image, ImageDraw, ImageFont
from io import BytesIO 




class VirtCanvas():

	def __init__(self, res=(800,240), background=None, color=(255,255,255)):
		self.res = res
		self.canvas = Image.new("RGBA", res, color)
		self.icon_size = (132,132)

		if background:
			self.canvas.alpha_composite(Image.open(background))

		# two ugly list comprehensions, they are calculating the centerpoints of the keys
		# take the width of the display and divide by number of keys, multiply by our iterator
		self.key_origins = []
		top = [(int(self.canvas.width / 6 * x), 0) for x in range(6)]
		bottom = [(int(self.canvas.width / 6 * x), int(self.canvas.height / 2)) for x in range(6)]

		# add our key origins to the list top then bottom
		self.key_origins += top
		self.key_origins += bottom


	def add_icon(self, path, keynum):
		# open our icon image then resize and resample
		icon_img = Image.open(path)
		icon_img = icon_img.resize(self.icon_size, resample=Image.Resampling.NEAREST)

		# blit the icon onto the canvas preserving transparency
		self.canvas.alpha_composite(icon_img.convert('RGBA'), dest=self.key_origins[keynum])


	def add_text(self, text, keynum):

		# print(f'add_text({text}, {keynum})')

		# font = ImageFont.truetype("NotoSansMono-Medium.ttf", 15)
		font = ImageFont.load_default()
		tile = Image.new('RGBA', self.icon_size, (255,255,255,0))
		tdraw = ImageDraw.Draw(tile)

		tdraw.text(self.key_origins[keynum], text,
				   fill=(255,255,255),
				   font=font)

		self.canvas.alpha_composite(tile.convert('RGBA'), dest=self.key_origins[keynum])

	def clear(self):
		pass


	def save(self):
		self.canvas.save('./panelimage.png', "PNG")


	def get_array(self):
		return list(self.canvas.getdata())


def get_img_bytes(path):
	return list(Image.open(path).getdata())