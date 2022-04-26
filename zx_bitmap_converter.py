#!/usr/bin/python3

#
# @Author: Skate/Plush
# @Date: 26/04/2022
#
# Usage:
# python zx_bitmap_converter.py <png_file> <output_folder>
#
# Example:
# py zx_bitmap_converter.py ../images/logo.png ../assets
# command will look for "logo.png" in images folder of the upper directory
# and generate output files to the assets folder of the upper directory
#

# include required libraries
import os
import sys
from PIL import Image

# at least two arguments are required
if len(sys.argv) <= 2:
	print('missing arguments')
	exit()

# get arguments
imageName = sys.argv[1]
outputPath = sys.argv[2]

# prepare input / output file names
sourceImage = imageName
outputBitmapFile = outputPath + "/bitmap.bin"
outputColorFile = outputPath + "/color.bin"

# ZX Spectrum bright palette colors
zxPalette = [0x000000, 0x0000ff, 0xff0000, 0xff00ff, 0x00ff00, 0x00ffff, 0xffff00, 0xffffff]

# character size definitions
charWidth = 8
charHeight = 8

# load bitmap frame image
img = Image.open(sourceImage).convert('RGBA')
imageWidth, imageHeight = img.size

# screen character block size definitions
blockWidth = int(imageWidth / charWidth)
blockHeight = int(imageHeight / charHeight)
blockSize = blockWidth * blockHeight

# output bitmap byte array
bitmapData = bytearray(b'\x00') * blockWidth * imageHeight

# output bitmap byte array
colorData = bytearray(b'\x00') * blockSize

# convert and output bitmap
for cx in range(blockWidth):
	# calculate X offset to look up and RGB pixel
	offsetX = cx * charWidth
	for cy in range(blockHeight):
		# calculate character Y offset of ZX Spectrum video memory
		offsetCY = (cy % charHeight) * blockWidth + int(cy / charHeight) * 0x800
		palette = []
		for y in range(charHeight):
			# calculate per pixel Y offset of ZX Spectrum video memory
			offsetY = offsetCY + y * 0x100

			# set video memory byte value to zero
			byteVal = 0
			# check bit by bit and find colors and video memory byte value
			for b in range(0, 8):
				# get corresponding RGB pixel value
				r, g, b, a = img.getpixel((offsetX + b, cy * charHeight + y))
				rgb = (r << 16) | (g << 8) | b

				# shift video memory byte bits to left
				byteVal = byteVal << 1

				# look up for RGB value in ZX Spectrum color palette
				# and get the color index
				try:
					ci = zxPalette.index(rgb)
				except ValueError as error:
					ci = 0
				pi = 0

				# look up the character palette index for the color
				# if it doesn't exist, add to the palette
				# no more than two colors are possible.
				try:
					pi = palette.index(ci)
				except ValueError as error:
					if(len(palette) < 2):
						palette.append(ci)
						pi = len(palette) - 1

				# put pixel value to video memory byte value
				byteVal |= pi
			
			# put video memory byte value to bitmap data array
			bitmapData[offsetY + cx] = byteVal

		# if char area is empty, add a default color as foreground color
		if(len(palette) < 2):
			palette.append(7)	# white color as empty area foreground color

		# calculate and add color to color data array
		colorData[cy * blockWidth + cx] = 0x40 + (palette[0] << 3) + palette[1]

# delete bitmap file
if os.path.exists(outputBitmapFile):
	os.remove(outputBitmapFile)

# delete color file
if os.path.exists(outputColorFile):
	os.remove(outputColorFile)

# create bitmap file
with open(outputBitmapFile, 'wb') as fileHandle:
	for bi in range(len(bitmapData)):
		bv = bitmapData[bi]
		fileHandle.write(bv.to_bytes(1, byteorder='big'))

# create color file
with open(outputColorFile, 'wb') as fileHandle:
	for bi in range(len(colorData)):
		bv = colorData[bi]
		fileHandle.write(bv.to_bytes(1, byteorder='big'))

# output success message
print('bitmap is successfully converted')