#!/usr/bin/env python3
"""The Passport Page of a Country That Isn't There.

Draws one invented passport spread (Republic of Talvera) as a PNG and
writes it to /output/entry.png. Pure standard library: the rasteriser,
the PNG encoder and the embedded bitmap font all live in this file, so
the program runs in a sandbox with no network and no third-party
packages.

The spread is built to read as a working document, not a poster:
  * data page: portrait, personal data, authority, MRZ with real ICAO
    check digits (7-3-1 weights), issue/expiry dates that agree;
  * visa page: a Dravnia visa sticker, entry/exit stamps from the
    three neighbouring countries, all dated after the passport was
    issued, plus a fee stamp and a conditions box (the telling detail:
    registration within 7 days, employment prohibited).
"""
import math
import os
import struct
import sys
import zlib

FONT = {
 12: {'h': 16, 'g': {
  ' ': (3, '0000000000000000'),
  '!': (3, '0002222222220000'),
  '"': (4, '0005550000000000'),
  '#': (7, '0000000a08043e143e10082800000000'),
  '$': (7, '0000081c2e28381c0e0a6a3c08000000'),
  '%': (9, '0000000000c20a40ac0c801001602904904e000000000000'),
  '&': (8, '000000384040443e6444443c00000000'),
  "'": (3, '0002220000000000'),
  '(': (4, '0022444444422000'),
  ')': (4, '0044422222444000'),
  '*': (7, '00000000000008083c1c040000000000'),
  '+': (7, '00000000000808083e08080000000000'),
  ',': (3, '0000000000026400'),
  '-': (3, '0000000070000000'),
  '.': (3, '0000000000220000'),
  '/': (4, '0001222444080000'),
  '0': (7, '0000001e322121212121321e00000000'),
  '1': (7, '0000000c3c0404040404040400000000'),
  '2': (7, '0000001c262202040818307e00000000'),
  '3': (7, '0000001c2602060c0642663c00000000'),
  '4': (7, '00000006060e0a12323f020200000000'),
  '5': (7, '0000003e20207c660242663c00000000'),
  '6': (7, '0000000e13212e332121331e00000000'),
  '7': (7, '0000007e06040c081810302000000000'),
  '8': (7, '0000001e2321331e3321231e00000000'),
  '9': (7, '0000001e332121331f21321c00000000'),
  ':': (3, '0000022000220000'),
  ';': (3, '0000022000024400'),
  '<': (7, '00000000000006182018060000000000'),
  '=': (7, '0000000000003e00003e000000000000'),
  '>': (7, '000000000000300c020c300000000000'),
  '?': (6, '0000000e111103020400040400000000'),
  '@': (11, '00000000007818c17e2da29229229637c1080f0000000000'),
  'A': (8, '00000018183c24247e4242c200000000'),
  'B': (7, '0000003c2222263c2321233e00000000'),
  'C': (9, '00000000003c04608208008008008204603c000000000000'),
  'D': (8, '0000007c424341414143427c00000000'),
  'E': (7, '0000003e2020203e2020203e00000000'),
  'F': (7, '0000003e2020203e2020202000000000'),
  'G': (9, '00000000003c04608208008e08208604603a000000000000'),
  'H': (9, '0000000000820820820820fe082082082082000000000000'),
  'I': (3, '0002222222220000'),
  'J': (7, '00000002020202020222261c00000000'),
  'K': (7, '00000021222428383824262300000000'),
  'L': (7, '00000020202020202020203e00000000'),
  'M': (10, '00000000018618618e14a14a14a172132132000000000000'),
  'N': (8, '00000062625252524a4a464600000000'),
  'O': (9, '00000000003c04208308108108108304203c000000000000'),
  'P': (7, '0000003e2321233e2020202000000000'),
  'Q': (9, '00000000003c04208308108108108304203e000000000000'),
  'R': (7, '0000003e2321233e2223212100000000'),
  'S': (6, '0000000e1311180e0301130e00000000'),
  'T': (8, '0000007f080808080808080800000000'),
  'U': (8, '00000042424242424242663c00000000'),
  'V': (7, '0000006121213312121e0c0c00000000'),
  'W': (11, '00000000063123127125334a14a14a18c18c000000000000'),
  'X': (8, '00000042642418181824464200000000'),
  'Y': (7, '000000432236141c0808080800000000'),
  'Z': (8, '0000007e060408181020607e00000000'),
  '[': (4, '0064444444446000'),
  '\\': (4, '0008844402200000'),
  ']': (4, '0062222222226000'),
  '^': (7, '00000000081414002200000000000000'),
  '_': (6, '0000000000000000000000001e000000'),
  '`': (4, '0000400000000000'),
  'a': (7, '00000000001c32021e22263e00000000'),
  'b': (7, '00000020202e33212121323e00000000'),
  'c': (7, '00000000001c32202020321c00000000'),
  'd': (8, '00000002023e66424242663e00000000'),
  'e': (7, '00000000001e32213f20331e00000000'),
  'f': (3, '0012272222220000'),
  'g': (8, '00000000003e66424242663e42663c00'),
  'h': (7, '00000020203c32222222222200000000'),
  'i': (3, '0002022222220000'),
  'j': (3, '0002022222222260'),
  'k': (6, '00000010101312141c14121300000000'),
  'l': (3, '0002222222230000'),
  'm': (11, '0000000000000003dc222222222222222222000000000000'),
  'n': (7, '00000000003c32222222222200000000'),
  'o': (7, '00000000001e33212121331e00000000'),
  'p': (7, '00000000002e33212121323e20202000'),
  'q': (8, '00000000003e66424242663e02020200'),
  'r': (4, '0000076444440000'),
  's': (6, '00000000000e13100e03110e00000000'),
  't': (4, '00044e4444460000'),
  'u': (7, '00000000002222222222261e00000000'),
  'v': (6, '0000000000213312121a0c0c00000000'),
  'w': (9, '0000000000000001191990a90aa0ae066046000000000000'),
  'x': (6, '000000000032160c0c1c162200000000'),
  'y': (6, '0000000000213312121a0c0c0c081000'),
  'z': (7, '00000000003e06040810303e00000000'),
  '{': (4, '0032222422223000'),
  '|': (3, '0022222222222220'),
  '}': (3, '0062222322226000'),
  '~': (7, '000000000000003a2e00000000000000'),
 }},
 24: {'h': 32, 'g': {
  ' ': (5, '0000000000000000000000000000000000000000000000000000000000000000'),
  '!': (5, '0000000000000000060606060606060606060606000e0e0e0000000000000000'),
  '"': (8, '0000000000000036363636363600000000000000000000000000000000000000'),
  '#': (15, '00000000000000000000000000000000009801900190013001300ffc0320032002601ff81ff80640064004c004c00c8000000000000000000000000000000000'),
  '$': (14, '000000000000000000000040004001f007fc0e4c0c4e0c440e400f4007e003f8007c004e004e08460c460e4e07fc03f000400040000000000000000000000000'),
  '%': (18, '0000000000000000000000000000000000000000078181fc3018c3018c601ccc00f8c00318000300003000067c00cee00cc6018c6030ce030fc060780000000000000000000000000000000000000000'),
  '&': (16, '0000000000000000000000000000000007e00fe01c00180018181c180ffe07ff1c18381830183018381838181ff807f800000000000000000000000000000000'),
  "'": (4, '00000006666660000000000000000000'),
  '(': (8, '000000000000040c0808181810101010101010101808080c0406000000000000'),
  ')': (8, '0000000000006020301010181808080808080818181010302060000000000000'),
  '*': (13, '0000000000000000000000000000000000000000000000000000004000400040064c03f800e001a0013003180000000000000000000000000000000000000000'),
  '+': (14, '00000000000000000000000000000000000000000000004000400040004000400ffc0ffc00400040004000400000000000000000000000000000000000000000'),
  ',': (5, '000000000000000000000000000000000000000000000c181818100000000000'),
  '-': (7, '000000000000000000000000000000003e3e0000000000000000000000000000'),
  '.': (5, '0000000000000000000000000000000000000000000e0e0e0000000000000000'),
  '/': (7, '00000000000000010303020606040c0c08181810303020606000000000000000'),
  '0': (14, '0000000000000000000000000000000003f007f80e1c0c0c1c0e1c0e18061806180618061c0e1c0e0c0c0e1c07f803f000000000000000000000000000000000'),
  '1': (14, '00000000000000000000000000000000007001f003b0073000300030003000300030003000300030003000300030003000000000000000000000000000000000'),
  '2': (14, '0000000000000000000000000000000003f007f80e1c0c1c1c0c000c00180038007000e001c0038007000e001ffc1ffc00000000000000000000000000000000'),
  '3': (14, '0000000000000000000000000000000003f007f80e1c0c0c000c001c00f800f00018000c000618061c0e0c0c0ffc03f000000000000000000000000000000000'),
  '4': (14, '0000000000000000000000000000000000180038007800f800d801980318071806180c181ffe1ffe001800180018001800000000000000000000000000000000'),
  '5': (14, '0000000000000000000000000000000007fe07fc0600060006000df00ffc0e0e0c0e000600060c060c0e0e0c07fc03f000000000000000000000000000000000'),
  '6': (14, '0000000000000000000000000000000001f007fc060e0c060ce01bf81e1c1c0e1c0e1806180618060c0e0e1c07f803f000000000000000000000000000000000'),
  '7': (14, '000000000000000000000000000000001ffe1ffe000c001c001800300030006000e000c001c001800380030006000e0000000000000000000000000000000000'),
  '8': (14, '0000000000000000000000000000000003f007f80e1c0c0c0c0c0e1c07f807f00e181c0c180618061c0e0c0e0ffc03f000000000000000000000000000000000'),
  '9': (14, '0000000000000000000000000000000003f007f80e1c1c0c180618061c061c0e0e1e07f601ce080c1c0c0c180ff803e000000000000000000000000000000000'),
  ':': (5, '00000000000000000000000e0e0e000000000000000e0e0e0000000000000000'),
  ';': (5, '00000000000000000000000e0e0e00000000000000000c0c1c18180000000000'),
  '<': (13, '0000000000000000000000000000000000000000000000000000000c003800e003800600070001c00070001c0006000000000000000000000000000000000000'),
  '=': (14, '000000000000000000000000000000000000000000000000000000000ffc0ffc000000000ffc0ffc000000000000000000000000000000000000000000000000'),
  '>': (14, '00000000000000000000000000000000000000000000000008000e00078001e00038001c003800f003c00f000c00000000000000000000000000000000000000'),
  '?': (12, '0000000000000000000000000f83fc70e70660600600c01c0380700600400000e00e00e0000000000000000000000000'),
  '@': (19, '000000000000000000000000000000000000038001ff0038380e00c0c004187a610fe2318622386223062230c6230c4239cc31f7810000180000c03007fe001f80000000000000000000000000000000'),
  'A': (15, '0000000000000000000000000000000001e001e001e0033003300330061806180ffc0ffc0c0c180e180618063007300300000000000000000000000000000000'),
  'B': (15, '000000000000000000000000000000001ff01ff8181c180c180c181c1ff81ff0181c180e18061806180e180e1ffc1ff000000000000000000000000000000000'),
  'C': (17, '0000000000000000000000000000000000000000007e001ff80381c0700c0600c0e0040c0000c0000c0000c0000e0040600c0701c0381801ff000fe00000000000000000000000000000000000000000'),
  'D': (17, '000000000000000000000000000000000000000007fc007ff0060380601c0600c0600e060060600606006060060600e0600c0601c0603807ff007fc00000000000000000000000000000000000000000'),
  'E': (14, '000000000000000000000000000000000ffe0ffe0c000c000c000c000c000ffc0ffc0c000c000c000c000c000ffe0ffe00000000000000000000000000000000'),
  'F': (14, '000000000000000000000000000000000ffe0ffe0c000c000c000c000c000ffc0ffc0c000c000c000c000c000c000c0000000000000000000000000000000000'),
  'G': (17, '0000000000000000000000000000000000000000007e001ff0038180700c0600c0e0000c0000c0000c0fc0c07c0e00c0600c0701c0383c01ffc00fcc0000000000000000000000000000000000000000'),
  'H': (17, '00000000000000000000000000000000000000000600c0600c0600c0600c0600c0600c0600c07ffc07ffc0600c0600c0600c0600c0600c0600c0600c0000000000000000000000000000000000000000'),
  'I': (6, '00000000000000000c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0000000000000000'),
  'J': (13, '00000000000000000000000000000000000c000c000c000c000c000c000c000c000c000c0c0c0c0c0e0c0e1c07f803f000000000000000000000000000000000'),
  'K': (14, '000000000000000000000000000000000c030c060c0e0c1c0c380c700ce00dc00fc00fe00e700c380c180c1c0c0e0c0700000000000000000000000000000000'),
  'L': (14, '000000000000000000000000000000000c000c000c000c000c000c000c000c000c000c000c000c000c000c000ffe0ffe00000000000000000000000000000000'),
  'M': (20, '00000000000000000000000000000000000000003c01c3c03c3c03c3e03c3606c3606c3306c330cc330cc318cc3198c3198c30d8c30f0c30f0c3070c0000000000000000000000000000000000000000'),
  'N': (17, '00000000000000000000000000000000000000000780c0780c07c0c06c0c0660c0660c0630c0630c0618c0618c060cc060cc0606c0607c0603c0603c0000000000000000000000000000000000000000'),
  'O': (18, '000000000000000000000000000000000000000000fc003ff0070380e01c0c00c1c00e180061800618006180061c00e0c00c0e01c0703803ff000fc00000000000000000000000000000000000000000'),
  'P': (14, '000000000000000000000000000000000ff80ffc0c0e0c060c060c060c0e0ffc0ff80c000c000c000c000c000c000c0000000000000000000000000000000000'),
  'Q': (18, '000000000000000000000000000000000000000000fc003ff0070380e01c0c00c1c00e180061800618006180061c00e0c00c0e01c0703803ff800ffe0000400000000000000000000000000000000000'),
  'R': (15, '000000000000000000000000000000001ff01ffc180e18061806180e180c1ff81ff8181c180c180c180c180c180e180600000000000000000000000000000000'),
  'S': (14, '0000000000000000000000000000000001f007fc0e0c0c0e0c060e00078003f000fc000e00061c061c060e0e07fc03f000000000000000000000000000000000'),
  'T': (15, '000000000000000000000000000000003fff3fff00c000c000c000c000c000c000c000c000c000c000c000c000c000c000000000000000000000000000000000'),
  'U': (16, '00000000000000000000000000000000300c300c300c300c300c300c300c300c300c300c300c300c381c1c1c0ff807e000000000000000000000000000000000'),
  'V': (15, '0000000000000000000000000000000030033807180618061c0e0c0c0c0c0e180618061807300330033001e001e001e000000000000000000000000000000000'),
  'W': (23, '000000000000000000000000000000000000000000000000301c07301e06381e0618360618360c18370c1c630c0c631c0c63180c61980ec19806c1b006c1b00780f00380f00380e0000000000000000000000000000000000000000000000000'),
  'X': (15, '000000000000000000000000000000003806180e0c0c0e180630037003e001c001c003e0033006380c181c0c180e300700000000000000000000000000000000'),
  'Y': (14, '00000000000000000000000000000000380718060c0e0e0c0618073803b001f001e000c000c000c000c000c000c000c000000000000000000000000000000000'),
  'Z': (15, '000000000000000000000000000000001ffe1ffe000c001c0038007000e000c001c0038007000e000c001c003ffe3ffe00000000000000000000000000000000'),
  '[': (8, '00000000001c1e10101010101010101010101010101010101c1e000000000000'),
  '\\': (7, '000000000000006060203030101818080c0c0406060203030100000000000000'),
  ']': (7, '00000000001c3c04040404040404040404040404040404041c3c000000000000'),
  '^': (14, '00000000000000000000000000000000000000c000c001e00120033003300618061804080c0c0000000000000000000000000000000000000000000000000000'),
  '_': (12, '0000000000000000000000000000000000000000000000000000000000000000000000007fe7fe000000000000000000'),
  '`': (7, '0000000000000010180800000000000000000000000000000000000000000000'),
  'a': (13, '0000000000000000000000000000000000000000000001f003f8061c060c000c00fc07fc0e0c0c0c0c1c0e1c07fc03ec00000000000000000000000000000000'),
  'b': (15, '0000000000000000000000000000180018001800180019f01ffc1e1c1c0e1c0618061806180618061c0e1e1c1ff819f000000000000000000000000000000000'),
  'c': (13, '0000000000000000000000000000000000000000000001f803fc070e06060e060c000c000c000e000e06070e03fc01f000000000000000000000000000000000'),
  'd': (15, '0000000000000000000000000000000c000c000c000c03ec0ffc1c1c181c380c300c300c300c380c381c1c3c0fec07cc00000000000000000000000000000000'),
  'e': (13, '0000000000000000000000000000000000000000000001f803fc070e06060c060fff0fff0c000c000e06060e03fc01f000000000000000000000000000000000'),
  'f': (8, '0000000000001e3e3030307e7e30303030303030303030300000000000000000'),
  'g': (15, '0000000000000000000000000000000000000000000003ec0ffc1c1c181c380c300c300c300c380c381c1c3c0fec07cc100c181c1c180ff807e0000000000000'),
  'h': (15, '0000000000000000000000001800180018001800180019f01ff81e1c1c1c1c0c180c180c180c180c180c180c180c180c00000000000000000000000000000000'),
  'i': (5, '00000000000000000c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0000000000000000'),
  'j': (5, '00000000000000000c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c1c18000000'),
  'k': (13, '000000000000000000000000000006000600060006000606060c06180630067006e007c007e007700638061c060e060700000000000000000000000000000000'),
  'l': (6, '000000000000000c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0e0f0000000000000000'),
  'm': (21, '00000000000000000000000000000000000000000000000000000000000000000006f8f807fdfc070f0c07070e06060e06060e06060e06060e06060e06060e06060e06060e06060e000000000000000000000000000000000000000000000000'),
  'n': (15, '0000000000000000000000000000000000000000000019f01ff81e1c1c1c1c0c180c180c180c180c180c180c180c180c00000000000000000000000000000000'),
  'o': (15, '0000000000000000000000000000000000000000000003e00ff81c1c180c380e300630063006380e180c1c1c0ff803e000000000000000000000000000000000'),
  'p': (15, '0000000000000000000000000000000000000000000019f01ffc1e1c1c0e1c0618061806180618061c0e1e1c1ff819f018001800180018001800000000000000'),
  'q': (15, '0000000000000000000000000000000000000000000003ec0ffc1c1c181c380c300c300c300c380c381c1c3c0fec07cc000c000c000c000c000c000000000000'),
  'r': (9, '00000000000000000000000000000000006e07e078070060060060060060060060060060000000000000000000000000'),
  's': (11, '0000000000000000000000000000000000f81fc38e3063801e00f801e00e3063861fe0f8000000000000000000000000'),
  't': (8, '00000000000000001818187e7e1818181818181818181e0e0000000000000000'),
  'u': (15, '00000000000000000000000000000000000000000000180c180c180c180c180c180c180c180c181c1c1c1c3c0ffc07cc00000000000000000000000000000000'),
  'v': (12, '000000000000000000000000000000000e0360760670630e30c38c1981981d80f00f0070000000000000000000000000'),
  'w': (19, '0000000000000000000000000000000000000000000000000000000707077070630f0630d8e38d8c18d8c1998c198d80d8d80d8d80f0f007070070700000000000000000000000000000000000000000'),
  'x': (12, '000000000000000000000000000000000e0e60c31c3981b00e00e00f01b039831c60ce0e000000000000000000000000'),
  'y': (12, '000000000000000000000000000000000c07c06e0660e60c30c3183181981b01f00f00e00600c00c0780700000000000'),
  'z': (12, '0000000000000000000000000000000003fe3fe00c01c0380300600e01c03803807fe7fe000000000000000000000000'),
  '{': (7, '0000000000020f0808080c0c04040c38180404040c0808080e07000000000000'),
  '|': (5, '0000000000040404040404040404040404040404040404040404040404000000'),
  '}': (8, '0000000000207818080818101010180c1c101010101808083870000000000000'),
  '~': (14, '00000000000000000000000000000000000000000000000000000000000007840fec087800000000000000000000000000000000000000000000000000000000'),
 }},
}

W, H = 1024, 1024
OUT = os.environ.get("OUTPUT_PATH", "/output/entry.png")


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, color=(255, 255, 255)):
        self.w, self.h = w, h
        self.px = bytearray(color * (w * h))

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def get(self, x, y):
        i = (y * self.w + x) * 3
        return self.px[i], self.px[i + 1], self.px[i + 2]

    def blend(self, x, y, color, alpha):
        """Alpha-blend color (0..1) onto pixel."""
        if 0 <= x < self.w and 0 <= y < self.h and alpha > 0:
            i = (y * self.w + x) * 3
            a = alpha
            self.px[i] = int(self.px[i] * (1 - a) + color[0] * a)
            self.px[i + 1] = int(self.px[i + 1] * (1 - a) + color[1] * a)
            self.px[i + 2] = int(self.px[i + 2] * (1 - a) + color[2] * a)

    def fill_rect(self, x0, y0, x1, y1, color):
        x0, x1 = max(0, x0), min(self.w, x1)
        y0, y1 = max(0, y0), min(self.h, y1)
        row = bytes(color) * (x1 - x0)
        for y in range(y0, y1):
            i = (y * self.w + x0) * 3
            self.px[i:i + len(row)] = row

    def rect(self, x0, y0, x1, y1, color, t=1):
        for k in range(t):
            self.hline(x0, y0 + k, x1, color)
            self.hline(x0, y1 - 1 - k, x1, color)
            self.vline(x0 + k, y0, y1, color)
            self.vline(x1 - 1 - k, y0, y1, color)

    def hline(self, x0, y, x1, color):
        if 0 <= y < self.h:
            self.fill_rect(min(x0, x1), y, max(x0, x1), y + 1, color)

    def vline(self, x, y0, y1, color):
        for y in range(max(0, y0), min(self.h, y1)):
            self.set(x, y, color)

    def line(self, x0, y0, x1, y1, color):
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def ellipse(self, cx, cy, rx, ry, color, fill=True):
        for y in range(cy - ry, cy + ry + 1):
            t = 1 - ((y - cy) / ry) ** 2
            if t < 0:
                continue
            dx = int(rx * math.sqrt(t))
            if fill:
                self.fill_rect(cx - dx, y, cx + dx + 1, y + 1, color)
            else:
                self.set(cx - dx, y, color)
                self.set(cx + dx, y, color)

    def circle(self, cx, cy, r, color, fill=True):
        self.ellipse(cx, cy, r, r, color, fill)

    def polygon(self, pts, color):
        """Scanline fill of a simple polygon."""
        ys = [p[1] for p in pts]
        for y in range(max(0, min(ys)), min(self.h, max(ys) + 1)):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                self.fill_rect(int(xs[k]), y, int(xs[k + 1]) + 1, y + 1, color)

    def blit(self, src, dx, dy, alpha=1.0):
        for y in range(src.h):
            for x in range(src.w):
                r, g, b = src.get(x, y)
                if (r, g, b) != (0, 0, 0):
                    self.blend(dx + x, dy + y, (r, g, b), alpha)

    def blit_rotated(self, src, cx, cy, angle_deg, alpha=1.0):
        """Paste src centred at (cx, cy), rotated by angle_deg."""
        a = math.radians(angle_deg)
        ca, sa = math.cos(a), math.sin(a)
        hw, hh = src.w / 2.0, src.h / 2.0
        r = int(math.hypot(hw, hh)) + 1
        for y in range(cy - r, cy + r + 1):
            for x in range(cx - r, cx + r + 1):
                lx, ly = x - cx, y - cy
                sx = int(lx * ca + ly * sa + hw)
                sy = int(-lx * sa + ly * ca + hh)
                if 0 <= sx < src.w and 0 <= sy < src.h:
                    c = src.get(sx, sy)
                    if c != (0, 0, 0):
                        self.blend(x, y, c, alpha)


# ------------------------------------------------------------------- text
def _glyph(size, ch):
    fd = FONT[size]
    g = fd["g"].get(ch)
    if g is None:
        g = fd["g"]["?"]
    return fd["h"], g


def text_width(text, size=24, scale=1, spacing=0, mono=None):
    w = 0
    for ch in text:
        _, (adv, _) = _glyph(size, ch)
        w += (mono if mono else adv) + spacing
    return (w - spacing if text else 0) * scale


def draw_text(cv, x, y, text, size=24, scale=1, color=(20, 20, 20),
              spacing=0, mono=None, alpha=1.0):
    """Draw text with its top at y (anchor 'la' baseline of the font)."""
    cx = x
    for ch in text:
        h, (adv, hexs) = _glyph(size, ch)
        nhex = (adv + 3) // 4
        for gy in range(h):
            row = int(hexs[gy * nhex:(gy + 1) * nhex] or "0", 16)
            for gx in range(adv):
                if row >> (adv - 1 - gx) & 1:
                    for sy in range(scale):
                        for sx in range(scale):
                            cv.blend(cx + gx * scale + sx,
                                     y + gy * scale + sy, color, alpha)
        cx += (mono if mono else adv) * scale + spacing * scale
    return cx


def text_centred(cv, cx, y, text, **kw):
    w = text_width(text, kw.get("size", 24), kw.get("scale", 1),
                   kw.get("spacing", 0), kw.get("mono"))
    return draw_text(cv, cx - w // 2, y, text, **kw)


# ---------------------------------------------------------------- helpers
def speckle(cv, x0, y0, x1, y1, amount=5, seed=7):
    s = seed
    for y in range(y0, y1):
        for x in range(x0, x1):
            s = (s * 1103515245 + 12345) & 0x7FFFFFFF
            d = (s % (2 * amount + 1)) - amount
            if d:
                r, g, b = cv.get(x, y)
                cv.set(x, y, (max(0, min(255, r + d)),
                              max(0, min(255, g + d)),
                              max(0, min(255, b + d))))


def vgrad(cv, x0, y0, x1, y1, top, bottom):
    for y in range(y0, y1):
        t = (y - y0) / max(1, y1 - y0 - 1)
        c = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        cv.fill_rect(x0, y, x1, y + 1, c)


def box_blur(cv, x0, y0, x1, y1, radius=2):
    w = x1 - x0
    src = [cv.get(x, y) for y in range(y0, y1) for x in range(x0, x1)]
    for y in range(y0, y1):
        for x in range(x0, x1):
            rs = gs = bs = n = 0
            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):
                    xx, yy = x + dx, y + dy
                    if x0 <= xx < x1 and y0 <= yy < y1:
                        r, g, b = src[(yy - y0) * w + (xx - x0)]
                        rs += r
                        gs += g
                        bs += b
                        n += 1
            cv.set(x, y, (rs // n, gs // n, bs // n))


def guilloche(cv, x0, y0, x1, y1, color, step=9):
    """Fine wavy security lines, low contrast."""
    for k in range(0, (y1 - y0) + (x1 - x0), step):
        for x in range(x0, x1):
            y = y0 + k + int(3 * math.sin((x - x0) / 26.0 + k))
            if y0 <= y < y1:
                cv.set(x, y, color)


# ------------------------------------------------------------ MRZ (ICAO)
def mrz_check(s):
    weights = (7, 3, 1)
    vals = {}
    for i in range(10):
        vals[str(i)] = i
    vals["<"] = 0
    for i, c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
        vals[c] = 10 + i
    return str(sum(vals[ch] * weights[i % 3] for i, ch in enumerate(s)) % 10)


def mrz_lines():
    line1 = "P<TVA" + "ILSEN<<MARA<ELIN"
    line1 = line1 + "<" * (44 - len(line1))
    doc = "TV483917<"  # 9-char document-number field
    doc_c = mrz_check(doc)
    dob = "940602"
    dob_c = mrz_check(dob)
    exp = "330313"
    exp_c = mrz_check(exp)
    pers = "<" * 14
    pers_c = mrz_check(pers)
    # composite check digit covers doc, dob, expiry and personal number
    comp = mrz_check(doc + doc_c + dob + dob_c + exp + exp_c + pers + pers_c)
    line2 = doc + doc_c + "TVA" + dob + dob_c + "F" + exp + exp_c
    line2 += pers + pers_c + comp
    assert len(line2) == 44, len(line2)
    return line1, line2


# --------------------------------------------------------------- portrait
def draw_portrait(cv, x0, y0, w, h):
    """Stylised passport photograph, softened with a blur."""
    vgrad(cv, x0, y0, x0 + w, y0 + h, (178, 196, 205), (138, 158, 170))
    speckle(cv, x0, y0, x0 + w, y0 + h, amount=4, seed=11)
    skin = (216, 169, 134)
    skin_d = (198, 148, 112)
    hair = (58, 42, 34)
    jacket = (38, 52, 74)
    # shoulders / jacket
    cv.polygon([(x0 + 8, y0 + h), (x0 + 34, y0 + int(h * 0.72)),
                (x0 + 62, y0 + int(h * 0.66)), (x0 + w - 62, y0 + int(h * 0.66)),
                (x0 + w - 34, y0 + int(h * 0.72)), (x0 + w - 8, y0 + h)],
               jacket)
    # shirt V + collar
    cv.polygon([(x0 + w // 2 - 16, y0 + int(h * 0.66)),
                (x0 + w // 2 + 16, y0 + int(h * 0.66)),
                (x0 + w // 2, y0 + int(h * 0.86))], (238, 238, 232))
    cv.polygon([(x0 + w // 2 - 5, y0 + int(h * 0.66)),
                (x0 + w // 2 + 5, y0 + int(h * 0.66)),
                (x0 + w // 2, y0 + int(h * 0.78))], (52, 60, 84))
    # neck
    cv.fill_rect(x0 + w // 2 - 13, y0 + int(h * 0.52),
                 x0 + w // 2 + 13, y0 + int(h * 0.68), skin_d)
    # head
    cx, cy = x0 + w // 2, y0 + int(h * 0.36)
    cv.ellipse(cx, cy, 44, 54, skin)
    # ears
    cv.ellipse(cx - 44, cy + 2, 7, 12, skin)
    cv.ellipse(cx + 44, cy + 2, 7, 12, skin)
    # hair: cap + side sweep
    cv.ellipse(cx, cy - 32, 46, 28, hair)
    cv.polygon([(cx - 46, cy - 24), (cx - 40, cy - 58), (cx + 10, cy - 64),
                (cx + 44, cy - 46), (cx + 46, cy - 18), (cx + 30, cy - 32),
                (cx - 10, cy - 40), (cx - 38, cy - 32)], hair)
    cv.polygon([(cx - 46, cy - 20), (cx - 30, cy - 36), (cx - 8, cy - 42),
                (cx - 34, cy - 24)], hair)
    # brows, eyes, nose, mouth
    for sgn in (-1, 1):
        ex = cx + sgn * 18
        cv.fill_rect(ex - 9, cy - 12, ex + 9, cy - 9, (70, 52, 40))
        cv.ellipse(ex, cy - 2, 6, 3, (245, 245, 240))
        cv.ellipse(ex, cy - 2, 3, 3, (32, 26, 22))
    cv.line(cx + 1, cy + 2, cx - 2, cy + 16, (176, 128, 96))
    cv.line(cx - 2, cy + 16, cx + 4, cy + 18, (176, 128, 96))
    cv.fill_rect(cx - 11, cy + 28, cx + 11, cy + 32, (150, 84, 72))
    # cheek shading
    cv.ellipse(cx - 28, cy + 14, 10, 6, (206, 150, 118))
    cv.ellipse(cx + 28, cy + 14, 10, 6, (206, 150, 118))
    box_blur(cv, x0, y0, x0 + w, y0 + h, radius=1)
    box_blur(cv, x0, y0, x0 + w, y0 + h, radius=1)


# ----------------------------------------------------------------- stamps
def oval_stamp(text_lines, w, h, color, size=12):
    """A small canvas holding an oval border stamp (transparent = black)."""
    c = Canvas(w, h, (0, 0, 0))
    c.ellipse(w // 2, h // 2, w // 2 - 2, h // 2 - 2, color, fill=False)
    c.ellipse(w // 2, h // 2, w // 2 - 6, h // 2 - 6, color, fill=False)
    y = (h - len(text_lines) * (size + 4)) // 2
    for ln in text_lines:
        text_centred(c, w // 2, y, ln, size=size, color=color)
        y += size + 4
    return c


def rect_stamp(text_lines, w, h, color, size=12):
    c = Canvas(w, h, (0, 0, 0))
    c.rect(2, 2, w - 2, h - 2, color, t=2)
    y = (h - len(text_lines) * (size + 4)) // 2
    for ln in text_lines:
        text_centred(c, w // 2, y, ln, size=size, color=color)
        y += size + 4
    return c


def visa_sticker(cv, x0, y0, w, h, angle):
    """Dravnia visa sticker, drawn on a temp canvas then rotated in."""
    c = Canvas(w, h, (0, 0, 0))
    vgrad(c, 0, 0, w, h, (36, 98, 120), (22, 62, 88))
    c.rect(3, 3, w - 3, h - 3, (214, 178, 110), t=2)
    c.rect(8, 8, w - 8, h - 8, (214, 178, 110), t=1)
    # small emblem: star over waves
    ex, ey = 26, 30
    c.circle(ex, ey, 12, (214, 178, 110), fill=False)
    c.line(ex, ey - 8, ex, ey + 8, (214, 178, 110))
    c.line(ex - 8, ey, ex + 8, ey, (214, 178, 110))
    c.line(ex - 6, ey - 6, ex + 6, ey + 6, (214, 178, 110))
    c.line(ex - 6, ey + 6, ex + 6, ey - 6, (214, 178, 110))
    gold = (232, 204, 138)
    draw_text(c, 46, 16, "KINGDOM OF DRAVNIA", size=12, color=gold)
    draw_text(c, 46, 34, "VISA", size=24, color=gold)
    draw_text(c, 14, 62, "MULTIPLE ENTRY  -  90 DAYS", size=12, color=(235, 240, 244))
    draw_text(c, 14, 82, "No. DV-221490", size=12, color=(235, 240, 244))
    draw_text(c, 14, 102, "VALID  01 JUL 2023 - 30 JUN 2024", size=12,
              color=(235, 240, 244))
    draw_text(c, 14, 122, "ISSUED AT PORT MERIDIAN", size=12, color=(235, 240, 244))
    draw_text(c, 14, 142, "HOLDER: ILSEN, MARA ELIN", size=12, color=(235, 240, 244))
    cv.blit_rotated(c, x0 + w // 2, y0 + h // 2, angle, alpha=0.96)


# ------------------------------------------------------------- data page
TEAL = (23, 77, 74)
GOLD = (176, 141, 74)
INK = (28, 30, 34)
GREY = (112, 106, 90)
PAPER = (243, 239, 226)


def field(cv, x, y, label, value, size=24):
    draw_text(cv, x, y, label, size=12, color=GREY)
    draw_text(cv, x, y + 17, value, size=size, color=INK)


def draw_data_page(cv, x0, y0, x1, y1):
    cv.fill_rect(x0, y0, x1, y1, PAPER)
    guilloche(cv, x0, y0, x1, y1, (228, 222, 200))
    # header
    draw_text(cv, x0 + 26, y0 + 22, "REPUBLIC OF TALVERA", size=24,
              color=TEAL, spacing=2)
    draw_text(cv, x0 + 26, y0 + 54, "PASSPORT  -  PASPORT", size=12,
              color=GOLD, spacing=3)
    # coat of arms: shield + star + waves
    ax, ay = x1 - 66, y0 + 46
    cv.polygon([(ax - 18, ay - 18), (ax + 18, ay - 18), (ax + 18, ay + 6),
                (ax, ay + 22), (ax - 18, ay + 6)], TEAL)
    cv.circle(ax, ay - 4, 6, GOLD, fill=False)
    cv.line(ax - 14, ay + 10, ax + 14, ay + 10, GOLD)
    cv.line(ax - 10, ay + 14, ax + 10, ay + 14, GOLD)
    cv.hline(x0 + 26, y0 + 76, x1 - 26, GOLD)
    cv.hline(x0 + 26, y0 + 79, x1 - 26, GOLD)
    # photo
    px, py, pw, ph = x0 + 26, y0 + 96, 168, 214
    draw_portrait(cv, px, py, pw, ph)
    cv.rect(px, py, px + pw, py + ph, INK, t=2)
    # small stamp overlapping the photo corner
    st = rect_stamp(["PORT", "MERIDIAN", "14 MAR 2023"], 92, 52,
                    (38, 74, 140), size=12)
    cv.blit_rotated(st, px + pw - 46, py + ph - 26, -14, alpha=0.55)
    # data fields, right of the photo
    fx = x0 + 216
    field(cv, fx, y0 + 96, "SURNAME / NOM", "ILSEN")
    field(cv, fx, y0 + 148, "GIVEN NAMES / PRENOMS", "MARA ELIN")
    field(cv, fx, y0 + 200, "NATIONALITY / NATIONALITE", "TALVERAN")
    field(cv, fx, y0 + 252, "DATE OF BIRTH / BORN", "02 JUN 1994")
    fx2 = x0 + 26
    field(cv, fx2, y0 + 330, "PLACE OF BIRTH / LIEU DE NAISSANCE",
          "KESTREL BAY")
    field(cv, fx2, y0 + 382, "SEX / SEXE", "F")
    field(cv, fx2 + 120, y0 + 382, "DOCUMENT No.", "TV 483 917")
    field(cv, fx2, y0 + 434, "DATE OF ISSUE / DELIVRE LE", "14 MAR 2023")
    field(cv, fx2 + 230, y0 + 434, "DATE OF EXPIRY / EXPIRE LE",
          "13 MAR 2033")
    field(cv, fx2, y0 + 486, "AUTHORITY / AUTORITE", "PORT MERIDIAN")
    # signature
    draw_text(cv, fx2, y0 + 540, "SIGNATURE OF BEARER", size=12, color=GREY)
    draw_text(cv, fx2, y0 + 556, "Mara Ilsen", size=24, color=INK)
    cv.hline(fx2, y0 + 588, fx2 + 200, INK)
    # MRZ band
    my = y1 - 78
    cv.fill_rect(x0 + 18, my, x1 - 18, y1 - 16, (232, 228, 212))
    l1, l2 = mrz_lines()
    draw_text(cv, x0 + 24, my + 12, l1, size=12, color=INK, mono=10)
    draw_text(cv, x0 + 24, my + 40, l2, size=12, color=INK, mono=10)


# ------------------------------------------------------------- visa page
def draw_visa_page(cv, x0, y0, x1, y1):
    cv.fill_rect(x0, y0, x1, y1, PAPER)
    guilloche(cv, x0, y0, x1, y1, (228, 222, 200))
    draw_text(cv, x0 + 26, y0 + 22, "VISAS", size=24, color=TEAL, spacing=4)
    draw_text(cv, x1 - 60, y0 + 26, "12", size=24, color=GREY)
    cv.hline(x0 + 26, y0 + 52, x1 - 26, GOLD)
    # faint watermark
    wm = Canvas(420, 60, (0, 0, 0))
    draw_text(wm, 0, 0, "TALVERA", size=24, scale=2, color=(216, 208, 182),
              spacing=4)
    cv.blit_rotated(wm, (x0 + x1) // 2, (y0 + y1) // 2, -24, alpha=0.5)
    # visa sticker, top left
    visa_sticker(cv, x0 + 30, y0 + 70, 300, 168, -3)
    # stamps, right column + lower area
    blue = (38, 74, 140)
    red = (168, 52, 44)
    purple = (104, 66, 140)
    green = (44, 110, 72)
    s1 = oval_stamp(["DRAVNIA", "ENTRY", "28 JUN 2023", "HALDOR PASS"],
                    150, 96, blue)
    cv.blit_rotated(s1, x0 + 408, y0 + 128, 12, alpha=0.62)
    s2 = oval_stamp(["DRAVNIA", "EXIT", "12 JUL 2023", "HALDOR PASS"],
                    150, 96, red)
    cv.blit_rotated(s2, x0 + 408, y0 + 246, -9, alpha=0.62)
    s3 = rect_stamp(["OSTMARK", "ENTRY", "09 OCT 2024", "BREGENZ"],
                    150, 92, purple)
    cv.blit_rotated(s3, x0 + 128, y0 + 300, 7, alpha=0.62)
    s4 = oval_stamp(["CALDOVA", "ENTRY", "17 FEB 2025"], 132, 84, green)
    cv.blit_rotated(s4, x0 + 330, y0 + 350, -13, alpha=0.62)
    s5 = oval_stamp(["CALDOVA", "EXIT", "02 MAR 2025"], 132, 84, green)
    cv.blit_rotated(s5, x0 + 420, y0 + 440, 10, alpha=0.62)
    # fee stamp
    s6 = rect_stamp(["FEE PAID", "25 TALER", "14 MAR 2023"], 120, 64, red)
    cv.blit_rotated(s6, x0 + 96, y0 + 452, -6, alpha=0.6)
    # telling detail: conditions box, bottom
    bx0, by0, bx1, by1 = x0 + 26, y1 - 168, x1 - 26, y1 - 22
    cv.fill_rect(bx0, by0, bx1, by1, (238, 234, 218))
    cv.rect(bx0, by0, bx1, by1, TEAL, t=1)
    draw_text(cv, bx0 + 12, by0 + 10, "CONDITIONS  -  TALVERAN / ENGLISH",
              size=12, color=TEAL, spacing=1)
    draw_text(cv, bx0 + 12, by0 + 32,
              "Holder must register with the local warden", size=12, color=INK)
    draw_text(cv, bx0 + 12, by0 + 50,
              "within 7 days of arrival. Employment", size=12, color=INK)
    draw_text(cv, bx0 + 12, by0 + 68,
              "prohibited. This passport remains the", size=12, color=INK)
    draw_text(cv, bx0 + 12, by0 + 86,
              "property of the Republic of Talvera.", size=12, color=INK)
    draw_text(cv, bx0 + 12, by0 + 112,
              "Pemegang wajib melapor dalam 7 hari.", size=12, color=GREY)


# -------------------------------------------------------------------- png
def png_bytes(cv):
    raw = bytearray()
    w = cv.w
    for y in range(cv.h):
        row = bytes(cv.px[y * w * 3:(y + 1) * w * 3])
        # Sub filter: first pixel raw, rest deltas
        sub = bytearray(row[:3])
        for i in range(3, len(row)):
            sub.append((row[i] - row[i - 3]) & 0xFF)
        raw.append(1)
        raw.extend(sub)
    best = None
    for level in (9, 6):
        comp = zlib.compress(bytes(raw), level)
        if best is None or len(comp) < len(best):
            best = comp
    ihdr = struct.pack(">IIBBBBB", w, cv.h, 8, 2, 0, 0, 0)

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", best) + chunk(b"IEND", b""))


def main():
    cv = Canvas(W, H, (24, 28, 36))
    speckle(cv, 0, 0, W, H, amount=3, seed=3)
    x0, y0, x1, y1 = 8, 154, 1016, 870
    mid = (x0 + x1) // 2
    # page shadows / gutter
    cv.fill_rect(x0 - 3, y0 - 3, x1 + 3, y1 + 3, (12, 14, 18))
    draw_data_page(cv, x0, y0, mid, y1)
    draw_visa_page(cv, mid, y0, x1, y1)
    cv.vline(mid - 1, y0, y1, (120, 112, 92))
    cv.vline(mid, y0, y1, (90, 84, 66))
    cv.rect(x0, y0, x1, y1, (12, 14, 18), t=2)
    data = png_bytes(cv)
    outdir = os.path.dirname(OUT)
    if outdir:
        os.makedirs(outdir, exist_ok=True)
    with open(OUT, "wb") as fh:
        fh.write(data)
    print(f"wrote {OUT}: {len(data)} bytes, {W}x{H}")


if __name__ == "__main__":
    main()
