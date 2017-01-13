#!/usr/bin/env python3

"""
    Colr - Named Color Data
    -Christopher Welborn 1-12-17
"""

# Named colors retrieved from the web and converted with colr.trans.
names = {
    'aliceblue': {
        'code': 231,
        'hexval': 'ffffff',
        'rgb': (255, 255, 255),
    },
    'antiquewhite': {
        'code': 230,
        'hexval': 'ffffd7',
        'rgb': (255, 255, 215),
    },
    'antiquewhite2': {
        'code': 224,
        'hexval': 'ffd7d7',
        'rgb': (255, 215, 215),
    },
    'antiquewhite3': {
        'code': 181,
        'hexval': 'd7afaf',
        'rgb': (215, 175, 175),
    },
    'antiquewhite4': {
        'code': 102,
        'hexval': '878787',
        'rgb': (135, 135, 135),
    },
    'aquamarine': {
        'code': 122,
        'hexval': '87ffd7',
        'rgb': (135, 255, 215),
    },
    'aquamarine2': {
        'code': 79,
        'hexval': '5fd7af',
        'rgb': (95, 215, 175),
    },
    'aquamarine3': {
        'code': 66,
        'hexval': '5f8787',
        'rgb': (95, 135, 135),
    },
    'azure': {
        'code': 231,
        'hexval': 'ffffff',
        'rgb': (255, 255, 255),
    },
    'azure2': {
        'code': 195,
        'hexval': 'd7ffff',
        'rgb': (215, 255, 255),
    },
    'azure3': {
        'code': 152,
        'hexval': 'afd7d7',
        'rgb': (175, 215, 215),
    },
    'azure4': {
        'code': 102,
        'hexval': '878787',
        'rgb': (135, 135, 135),
    },
    'beige': {
        'code': 230,
        'hexval': 'ffffd7',
        'rgb': (255, 255, 215),
    },
    'bisque': {
        'code': 224,
        'hexval': 'ffd7d7',
        'rgb': (255, 215, 215),
    },
    'bisque2': {
        'code': 223,
        'hexval': 'ffd7af',
        'rgb': (255, 215, 175),
    },
    'bisque3': {
        'code': 181,
        'hexval': 'd7afaf',
        'rgb': (215, 175, 175),
    },
    'bisque4': {
        'code': 101,
        'hexval': '87875f',
        'rgb': (135, 135, 95),
    },
    'black': {
        'code': 16,
        'hexval': '000000',
        'rgb': (0, 0, 0),
    },
    'blanchedalmond': {
        'code': 230,
        'hexval': 'ffffd7',
        'rgb': (255, 255, 215),
    },
    'blue': {
        'code': 21,
        'hexval': '0000ff',
        'rgb': (0, 0, 255),
    },
    'blue2': {
        'code': 20,
        'hexval': '0000d7',
        'rgb': (0, 0, 215),
    },
    'blue3': {
        'code': 18,
        'hexval': '000087',
        'rgb': (0, 0, 135),
    },
    'blueviolet': {
        'code': 92,
        'hexval': '8700d7',
        'rgb': (135, 0, 215),
    },
    'brown': {
        'code': 124,
        'hexval': 'af0000',
        'rgb': (175, 0, 0),
    },
    'brown2': {
        'code': 203,
        'hexval': 'ff5f5f',
        'rgb': (255, 95, 95),
    },
    'brown3': {
        'code': 167,
        'hexval': 'd75f5f',
        'rgb': (215, 95, 95),
    },
    'brown4': {
        'code': 88,
        'hexval': '870000',
        'rgb': (135, 0, 0),
    },
    'burlywood': {
        'code': 180,
        'hexval': 'd7af87',
        'rgb': (215, 175, 135),
    },
    'burlywood2': {
        'code': 223,
        'hexval': 'ffd7af',
        'rgb': (255, 215, 175),
    },
    'burlywood3': {
        'code': 222,
        'hexval': 'ffd787',
        'rgb': (255, 215, 135),
    },
    'burlywood4': {
        'code': 180,
        'hexval': 'd7af87',
        'rgb': (215, 175, 135),
    },
    'burlywood5': {
        'code': 101,
        'hexval': '87875f',
        'rgb': (135, 135, 95),
    },
    'cadetblue': {
        'code': 73,
        'hexval': '5fafaf',
        'rgb': (95, 175, 175),
    },
    'cadetblue2': {
        'code': 123,
        'hexval': '87ffff',
        'rgb': (135, 255, 255),
    },
    'cadetblue3': {
        'code': 117,
        'hexval': '87d7ff',
        'rgb': (135, 215, 255),
    },
    'cadetblue4': {
        'code': 116,
        'hexval': '87d7d7',
        'rgb': (135, 215, 215),
    },
    'cadetblue5': {
        'code': 66,
        'hexval': '5f8787',
        'rgb': (95, 135, 135),
    },
    'chartreuse': {
        'code': 118,
        'hexval': '87ff00',
        'rgb': (135, 255, 0),
    },
    'chartreuse2': {
        'code': 76,
        'hexval': '5fd700',
        'rgb': (95, 215, 0),
    },
    'chartreuse3': {
        'code': 64,
        'hexval': '5f8700',
        'rgb': (95, 135, 0),
    },
    'chocolate': {
        'code': 166,
        'hexval': 'd75f00',
        'rgb': (215, 95, 0),
    },
    'chocolate2': {
        'code': 208,
        'hexval': 'ff8700',
        'rgb': (255, 135, 0),
    },
    'chocolate3': {
        'code': 166,
        'hexval': 'd75f00',
        'rgb': (215, 95, 0),
    },
    'chocolate4': {
        'code': 94,
        'hexval': '875f00',
        'rgb': (135, 95, 0),
    },
    'coral': {
        'code': 203,
        'hexval': 'ff5f5f',
        'rgb': (255, 95, 95),
    },
    'coral2': {
        'code': 209,
        'hexval': 'ff875f',
        'rgb': (255, 135, 95),
    },
    'coral3': {
        'code': 167,
        'hexval': 'd75f5f',
        'rgb': (215, 95, 95),
    },
    'coral4': {
        'code': 94,
        'hexval': '875f00',
        'rgb': (135, 95, 0),
    },
    'cornflowerblue': {
        'code': 69,
        'hexval': '5f87ff',
        'rgb': (95, 135, 255),
    },
    'cornsilk': {
        'code': 230,
        'hexval': 'ffffd7',
        'rgb': (255, 255, 215),
    },
    'cornsilk2': {
        'code': 224,
        'hexval': 'ffd7d7',
        'rgb': (255, 215, 215),
    },
    'cornsilk3': {
        'code': 187,
        'hexval': 'd7d7af',
        'rgb': (215, 215, 175),
    },
    'cornsilk4': {
        'code': 102,
        'hexval': '878787',
        'rgb': (135, 135, 135),
    },
    'cyan': {
        'code': 51,
        'hexval': '00ffff',
        'rgb': (0, 255, 255),
    },
    'cyan2': {
        'code': 44,
        'hexval': '00d7d7',
        'rgb': (0, 215, 215),
    },
    'cyan3': {
        'code': 30,
        'hexval': '008787',
        'rgb': (0, 135, 135),
    },
    'darkblue': {
        'code': 18,
        'hexval': '000087',
        'rgb': (0, 0, 135),
    },
    'darkcyan': {
        'code': 30,
        'hexval': '008787',
        'rgb': (0, 135, 135),
    },
    'darkgoldenrod': {
        'code': 136,
        'hexval': 'af8700',
        'rgb': (175, 135, 0),
    },
    'darkgoldenrod2': {
        'code': 214,
        'hexval': 'ffaf00',
        'rgb': (255, 175, 0),
    },
    'darkgoldenrod3': {
        'code': 172,
        'hexval': 'd78700',
        'rgb': (215, 135, 0),
    },
    'darkgoldenrod4': {
        'code': 94,
        'hexval': '875f00',
        'rgb': (135, 95, 0),
    },
    'darkgray': {
        'code': 145,
        'hexval': 'afafaf',
        'rgb': (175, 175, 175),
    },
    'darkgreen': {
        'code': 22,
        'hexval': '005f00',
        'rgb': (0, 95, 0),
    },
    'darkgrey': {
        'code': 145,
        'hexval': 'afafaf',
        'rgb': (175, 175, 175),
    },
    'darkkhaki': {
        'code': 143,
        'hexval': 'afaf5f',
        'rgb': (175, 175, 95),
    },
    'darkmagenta': {
        'code': 90,
        'hexval': '870087',
        'rgb': (135, 0, 135),
    },
    'darkolivegreen': {
        'code': 58,
        'hexval': '5f5f00',
        'rgb': (95, 95, 0),
    },
    'darkolivegreen2': {
        'code': 191,
        'hexval': 'd7ff5f',
        'rgb': (215, 255, 95),
    },
    'darkolivegreen3': {
        'code': 155,
        'hexval': 'afff5f',
        'rgb': (175, 255, 95),
    },
    'darkolivegreen4': {
        'code': 149,
        'hexval': 'afd75f',
        'rgb': (175, 215, 95),
    },
    'darkolivegreen5': {
        'code': 65,
        'hexval': '5f875f',
        'rgb': (95, 135, 95),
    },
    'darkorange': {
        'code': 208,
        'hexval': 'ff8700',
        'rgb': (255, 135, 0),
    },
    'darkorange2': {
        'code': 166,
        'hexval': 'd75f00',
        'rgb': (215, 95, 0),
    },
    'darkorange3': {
        'code': 94,
        'hexval': '875f00',
        'rgb': (135, 95, 0),
    },
    'darkorchid': {
        'code': 98,
        'hexval': '875fd7',
        'rgb': (135, 95, 215),
    },
    'darkorchid2': {
        'code': 135,
        'hexval': 'af5fff',
        'rgb': (175, 95, 255),
    },
    'darkorchid3': {
        'code': 98,
        'hexval': '875fd7',
        'rgb': (135, 95, 215),
    },
    'darkorchid4': {
        'code': 54,
        'hexval': '5f0087',
        'rgb': (95, 0, 135),
    },
    'darkred': {
        'code': 88,
        'hexval': '870000',
        'rgb': (135, 0, 0),
    },
    'darksalmon': {
        'code': 174,
        'hexval': 'd78787',
        'rgb': (215, 135, 135),
    },
    'darkseagreen': {
        'code': 108,
        'hexval': '87af87',
        'rgb': (135, 175, 135),
    },
    'darkseagreen2': {
        'code': 157,
        'hexval': 'afffaf',
        'rgb': (175, 255, 175),
    },
    'darkseagreen3': {
        'code': 151,
        'hexval': 'afd7af',
        'rgb': (175, 215, 175),
    },
    'darkseagreen4': {
        'code': 65,
        'hexval': '5f875f',
        'rgb': (95, 135, 95),
    },
    'darkslateblue': {
        'code': 60,
        'hexval': '5f5f87',
        'rgb': (95, 95, 135),
    },
    'darkslategray': {
        'code': 23,
        'hexval': '005f5f',
        'rgb': (0, 95, 95),
    },
    'darkslategray2': {
        'code': 123,
        'hexval': '87ffff',
        'rgb': (135, 255, 255),
    },
    'darkslategray3': {
        'code': 116,
        'hexval': '87d7d7',
        'rgb': (135, 215, 215),
    },
    'darkslategray4': {
        'code': 66,
        'hexval': '5f8787',
        'rgb': (95, 135, 135),
    },
    'darkslategrey': {
        'code': 23,
        'hexval': '005f5f',
        'rgb': (0, 95, 95),
    },
    'darkturquoise': {
        'code': 44,
        'hexval': '00d7d7',
        'rgb': (0, 215, 215),
    },
    'darkviolet': {
        'code': 92,
        'hexval': '8700d7',
        'rgb': (135, 0, 215),
    },
    'debianred': {
        'code': 161,
        'hexval': 'd7005f',
        'rgb': (215, 0, 95),
    },
    'deeppink': {
        'code': 198,
        'hexval': 'ff0087',
        'rgb': (255, 0, 135),
    },
    'deeppink2': {
        'code': 162,
        'hexval': 'd70087',
        'rgb': (215, 0, 135), },
    'deeppink3': {
        'code': 89,
        'hexval': '87005f',
        'rgb': (135, 0, 95),
    },
    'deepskyblue': {
        'code': 39,
        'hexval': '00afff',
        'rgb': (0, 175, 255),
    },
    'deepskyblue2': {
        'code': 32,
        'hexval': '0087d7',
        'rgb': (0, 135, 215),
    },
    'deepskyblue3': {
        'code': 24,
        'hexval': '005f87',
        'rgb': (0, 95, 135),
    },
    'dimgrey': {
        'code': 59,
        'hexval': '5f5f5f',
        'rgb': (95, 95, 95),
    },
    'dodgerblue': {
        'code': 33,
        'hexval': '0087ff',
        'rgb': (0, 135, 255),
    },
    'dodgerblue2': {
        'code': 32,
        'hexval': '0087d7',
        'rgb': (0, 135, 215),
    },
    'dodgerblue3': {
        'code': 24,
        'hexval': '005f87',
        'rgb': (0, 95, 135),
    },
    'firebrick': {
        'code': 124,
        'hexval': 'af0000',
        'rgb': (175, 0, 0),
    },
    'firebrick2': {
        'code': 203,
        'hexval': 'ff5f5f',
        'rgb': (255, 95, 95),
    },
    'firebrick3': {
        'code': 160,
        'hexval': 'd70000',
        'rgb': (215, 0, 0),
    },
    'firebrick4': {
        'code': 88,
        'hexval': '870000',
        'rgb': (135, 0, 0),
    },
    'floralwhite': {
        'code': 231,
        'hexval': 'ffffff',
        'rgb': (255, 255, 255),
    },
    'forestgreen': {
        'code': 28,
        'hexval': '008700',
        'rgb': (0, 135, 0),
    },
    'gainsboro': {
        'code': 188,
        'hexval': 'd7d7d7',
        'rgb': (215, 215, 215),
    },
    'ghostwhite': {
        'code': 231,
        'hexval': 'ffffff',
        'rgb': (255, 255, 255),
    },
    'gold': {
        'code': 220,
        'hexval': 'ffd700',
        'rgb': (255, 215, 0),
    },
    'gold2': {
        'code': 178,
        'hexval': 'd7af00',
        'rgb': (215, 175, 0),
    },
    'gold3': {
        'code': 100,
        'hexval': '878700',
        'rgb': (135, 135, 0),
    },
    'goldenrod': {
        'code': 178,
        'hexval': 'd7af00',
        'rgb': (215, 175, 0),
    },
    'goldenrod2': {
        'code': 214,
        'hexval': 'ffaf00',
        'rgb': (255, 175, 0),
    },
    'goldenrod3': {
        'code': 178,
        'hexval': 'd7af00',
        'rgb': (215, 175, 0),
    },
    'goldenrod4': {
        'code': 94,
        'hexval': '875f00',
        'rgb': (135, 95, 0),
    },
    'gray': {
        'code': 145,
        'hexval': 'afafaf',
        'rgb': (175, 175, 175),
    },
    'gray100': {
        'code': 231,
        'hexval': 'ffffff',
        'rgb': (255, 255, 255),
    },
    'gray37': {
        'code': 59,
        'hexval': '5f5f5f',
        'rgb': (95, 95, 95),
    },
    'gray50': {
        'code': 102,
        'hexval': '878787',
        'rgb': (135, 135, 135),
    },
    'gray59': {
        'code': 102,
        'hexval': '878787',
        'rgb': (135, 135, 135),
    },
    'green': {
        'code': 46,
        'hexval': '00ff00',
        'rgb': (0, 255, 0),
    },
    'green2': {
        'code': 40,
        'hexval': '00d700',
        'rgb': (0, 215, 0),
    },
    'green3': {
        'code': 28,
        'hexval': '008700',
        'rgb': (0, 135, 0),
    },
    'greenyellow': {
        'code': 154,
        'hexval': 'afff00',
        'rgb': (175, 255, 0),
    },
    'grey': {
        'code': 145,
        'hexval': 'afafaf',
        'rgb': (175, 175, 175),
    },
    'grey100': {
        'code': 231,
        'hexval': 'ffffff',
        'rgb': (255, 255, 255),
    },
    'grey37': {
        'code': 59,
        'hexval': '5f5f5f',
        'rgb': (95, 95, 95),
    },
    'grey50': {
        'code': 102,
        'hexval': '878787',
        'rgb': (135, 135, 135),
    },
    'grey59': {
        'code': 102,
        'hexval': '878787',
        'rgb': (135, 135, 135),
    },
    'honeydew2': {
        'code': 194,
        'hexval': 'd7ffd7',
        'rgb': (215, 255, 215),
    },
    'honeydew3': {
        'code': 151,
        'hexval': 'afd7af',
        'rgb': (175, 215, 175),
    },
    'honeydew4': {
        'code': 102,
        'hexval': '878787',
        'rgb': (135, 135, 135),
    },
    'hotpink': {
        'code': 205,
        'hexval': 'ff5faf',
        'rgb': (255, 95, 175),
    },
    'hotpink2': {
        'code': 168,
        'hexval': 'd75f87',
        'rgb': (215, 95, 135),
    },
    'hotpink3': {
        'code': 95,
        'hexval': '875f5f',
        'rgb': (135, 95, 95),
    },
    'indianred': {
        'code': 167,
        'hexval': 'd75f5f',
        'rgb': (215, 95, 95),
    },
    'indianred2': {
        'code': 203,
        'hexval': 'ff5f5f',
        'rgb': (255, 95, 95),
    },
    'indianred3': {
        'code': 167,
        'hexval': 'd75f5f',
        'rgb': (215, 95, 95),
    },
    'indianred4': {
        'code': 95,
        'hexval': '875f5f',
        'rgb': (135, 95, 95),
    },
    'ivory': {
        'code': 231,
        'hexval': 'ffffff',
        'rgb': (255, 255, 255),
    },
    'ivory2': {
        'code': 230,
        'hexval': 'ffffd7',
        'rgb': (255, 255, 215),
    },
    'ivory3': {
        'code': 187,
        'hexval': 'd7d7af',
        'rgb': (215, 215, 175),
    },
    'ivory4': {
        'code': 102,
        'hexval': '878787',
        'rgb': (135, 135, 135),
    },
    'khaki': {
        'code': 222,
        'hexval': 'ffd787',
        'rgb': (255, 215, 135),
    },
    'khaki2': {
        'code': 228,
        'hexval': 'ffff87',
        'rgb': (255, 255, 135),
    },
    'khaki3': {
        'code': 186,
        'hexval': 'd7d787',
        'rgb': (215, 215, 135),
    },
    'khaki4': {
        'code': 101,
        'hexval': '87875f',
        'rgb': (135, 135, 95),
    },
    'lavender': {
        'code': 189,
        'hexval': 'd7d7ff',
        'rgb': (215, 215, 255),
    },
    'lavenderblush': {
        'code': 231,
        'hexval': 'ffffff',
        'rgb': (255, 255, 255),
    },
    'lavenderblush2': {
        'code': 224,
        'hexval': 'ffd7d7',
        'rgb': (255, 215, 215),
    },
    'lavenderblush3': {
        'code': 182,
        'hexval': 'd7afd7',
        'rgb': (215, 175, 215),
    },
    'lavenderblush4': {
        'code': 102,
        'hexval': '878787',
        'rgb': (135, 135, 135),
    },
    'lawngreen': {
        'code': 118,
        'hexval': '87ff00',
        'rgb': (135, 255, 0),
    },
    'lemonchiffon': {
        'code': 230,
        'hexval': 'ffffd7',
        'rgb': (255, 255, 215),
    },
    'lemonchiffon2': {
        'code': 223,
        'hexval': 'ffd7af',
        'rgb': (255, 215, 175),
    },
    'lemonchiffon3': {
        'code': 187,
        'hexval': 'd7d7af',
        'rgb': (215, 215, 175),
    },
    'lemonchiffon4': {
        'code': 101,
        'hexval': '87875f',
        'rgb': (135, 135, 95),
    },
    'lightblue': {
        'code': 152,
        'hexval': 'afd7d7',
        'rgb': (175, 215, 215),
    },
    'lightblue2': {
        'code': 159,
        'hexval': 'afffff',
        'rgb': (175, 255, 255),
    },
    'lightblue3': {
        'code': 153,
        'hexval': 'afd7ff',
        'rgb': (175, 215, 255),
    },
    'lightblue4': {
        'code': 110,
        'hexval': '87afd7',
        'rgb': (135, 175, 215),
    },
    'lightblue5': {
        'code': 66,
        'hexval': '5f8787',
        'rgb': (95, 135, 135),
    },
    'lightcoral': {
        'code': 210,
        'hexval': 'ff8787',
        'rgb': (255, 135, 135),
    },
    'lightcyan': {
        'code': 195,
        'hexval': 'd7ffff',
        'rgb': (215, 255, 255),
    },
    'lightcyan3': {
        'code': 152,
        'hexval': 'afd7d7',
        'rgb': (175, 215, 215),
    },
    'lightcyan4': {
        'code': 102,
        'hexval': '878787',
        'rgb': (135, 135, 135),
    },
    'lightgoldenrod': {
        'code': 222,
        'hexval': 'ffd787',
        'rgb': (255, 215, 135),
    },
    'lightgoldenrod2': {
        'code': 228,
        'hexval': 'ffff87',
        'rgb': (255, 255, 135),
    },
    'lightgoldenrod3': {
        'code': 179,
        'hexval': 'd7af5f',
        'rgb': (215, 175, 95),
    },
    'lightgoldenrod4': {
        'code': 101,
        'hexval': '87875f',
        'rgb': (135, 135, 95),
    },
    'lightgoldenrodyellow': {
        'code': 230,
        'hexval': 'ffffd7',
        'rgb': (255, 255, 215),
    },
    'lightgray': {
        'code': 188,
        'hexval': 'd7d7d7',
        'rgb': (215, 215, 215),
    },
    'lightgreen': {
        'code': 120,
        'hexval': '87ff87',
        'rgb': (135, 255, 135),
    },
    'lightgrey': {
        'code': 188,
        'hexval': 'd7d7d7',
        'rgb': (215, 215, 215),
    },
    'lightpink': {
        'code': 217,
        'hexval': 'ffafaf',
        'rgb': (255, 175, 175),
    },
    'lightpink2': {
        'code': 174,
        'hexval': 'd78787',
        'rgb': (215, 135, 135),
    },
    'lightpink3': {
        'code': 95,
        'hexval': '875f5f',
        'rgb': (135, 95, 95),
    },
    'lightsalmon': {
        'code': 216,
        'hexval': 'ffaf87',
        'rgb': (255, 175, 135),
    },
    'lightsalmon2': {
        'code': 209,
        'hexval': 'ff875f',
        'rgb': (255, 135, 95),
    },
    'lightsalmon3': {
        'code': 173,
        'hexval': 'd7875f',
        'rgb': (215, 135, 95),
    },
    'lightsalmon4': {
        'code': 95,
        'hexval': '875f5f',
        'rgb': (135, 95, 95),
    },
    'lightseagreen': {
        'code': 37,
        'hexval': '00afaf',
        'rgb': (0, 175, 175),
    },
    'lightskyblue': {
        'code': 117,
        'hexval': '87d7ff',
        'rgb': (135, 215, 255),
    },
    'lightskyblue2': {
        'code': 153,
        'hexval': 'afd7ff',
        'rgb': (175, 215, 255),
    },
    'lightskyblue3': {
        'code': 110,
        'hexval': '87afd7',
        'rgb': (135, 175, 215),
    },
    'lightskyblue4': {
        'code': 66,
        'hexval': '5f8787',
        'rgb': (95, 135, 135),
    },
    'lightslateblue': {
        'code': 99,
        'hexval': '875fff',
        'rgb': (135, 95, 255),
    },
    'lightslategray': {
        'code': 102,
        'hexval': '878787',
        'rgb': (135, 135, 135),
    },
    'lightsteelblue': {
        'code': 152,
        'hexval': 'afd7d7',
        'rgb': (175, 215, 215),
    },
    'lightsteelblue2': {
        'code': 189,
        'hexval': 'd7d7ff',
        'rgb': (215, 215, 255),
    },
    'lightsteelblue3': {
        'code': 153,
        'hexval': 'afd7ff',
        'rgb': (175, 215, 255),
    },
    'lightsteelblue4': {
        'code': 146,
        'hexval': 'afafd7',
        'rgb': (175, 175, 215),
    },
    'lightsteelblue5': {
        'code': 66,
        'hexval': '5f8787',
        'rgb': (95, 135, 135),
    },
    'lightyellow': {
        'code': 230,
        'hexval': 'ffffd7',
        'rgb': (255, 255, 215),
    },
    'lightyellow2': {
        'code': 230,
        'hexval': 'ffffd7',
        'rgb': (255, 255, 215),
    },
    'lightyellow3': {
        'code': 187,
        'hexval': 'd7d7af',
        'rgb': (215, 215, 175),
    },
    'lightyellow4': {
        'code': 102,
        'hexval': '878787',
        'rgb': (135, 135, 135),
    },
    'limegreen': {
        'code': 77,
        'hexval': '5fd75f',
        'rgb': (95, 215, 95),
    },
    'linen': {
        'code': 230,
        'hexval': 'ffffd7',
        'rgb': (255, 255, 215),
    },
    'magenta': {
        'code': 201,
        'hexval': 'ff00ff',
        'rgb': (255, 0, 255),
    },
    'magenta2': {
        'code': 164,
        'hexval': 'd700d7',
        'rgb': (215, 0, 215),
    },
    'magenta3': {
        'code': 90,
        'hexval': '870087',
        'rgb': (135, 0, 135),
    },
    'maroon': {
        'code': 131,
        'hexval': 'af5f5f',
        'rgb': (175, 95, 95),
    },
    'maroon2': {
        'code': 205,
        'hexval': 'ff5faf',
        'rgb': (255, 95, 175),
    },
    'maroon3': {
        'code': 162,
        'hexval': 'd70087',
        'rgb': (215, 0, 135),
    },
    'maroon4': {
        'code': 89,
        'hexval': '87005f',
        'rgb': (135, 0, 95),
    },
    'mediumaquamarine': {
        'code': 79,
        'hexval': '5fd7af',
        'rgb': (95, 215, 175),
    },
    'mediumblue': {
        'code': 20,
        'hexval': '0000d7',
        'rgb': (0, 0, 215),
    },
    'mediumorchid': {
        'code': 134,
        'hexval': 'af5fd7',
        'rgb': (175, 95, 215),
    },
    'mediumorchid2': {
        'code': 171,
        'hexval': 'd75fff',
        'rgb': (215, 95, 255),
    },
    'mediumorchid3': {
        'code': 134,
        'hexval': 'af5fd7',
        'rgb': (175, 95, 215),
    },
    'mediumorchid4': {
        'code': 96,
        'hexval': '875f87',
        'rgb': (135, 95, 135),
    },
    'mediumpurple': {
        'code': 98,
        'hexval': '875fd7',
        'rgb': (135, 95, 215),
    },
    'mediumpurple3': {
        'code': 141,
        'hexval': 'af87ff',
        'rgb': (175, 135, 255),
    },
    'mediumpurple4': {
        'code': 98,
        'hexval': '875fd7',
        'rgb': (135, 95, 215),
    },
    'mediumpurple5': {
        'code': 60,
        'hexval': '5f5f87',
        'rgb': (95, 95, 135),
    },
    'mediumseagreen': {
        'code': 71,
        'hexval': '5faf5f',
        'rgb': (95, 175, 95),
    },
    'mediumslateblue': {
        'code': 99,
        'hexval': '875fff',
        'rgb': (135, 95, 255),
    },
    'mediumspringgreen': {
        'code': 48,
        'hexval': '00ff87',
        'rgb': (0, 255, 135),
    },
    'mediumturquoise': {
        'code': 80,
        'hexval': '5fd7d7',
        'rgb': (95, 215, 215),
    },
    'mediumvioletred': {
        'code': 162,
        'hexval': 'd70087',
        'rgb': (215, 0, 135),
    },
    'midnightblue': {
        'code': 17,
        'hexval': '00005f',
        'rgb': (0, 0, 95),
    },
    'mintcream': {
        'code': 231,
        'hexval': 'ffffff',
        'rgb': (255, 255, 255),
    },
    'mistyrose': {
        'code': 224,
        'hexval': 'ffd7d7',
        'rgb': (255, 215, 215),
    },
    'mistyrose2': {
        'code': 181,
        'hexval': 'd7afaf',
        'rgb': (215, 175, 175),
    },
    'mistyrose3': {
        'code': 102,
        'hexval': '878787',
        'rgb': (135, 135, 135),
    },
    'moccasin': {
        'code': 223,
        'hexval': 'ffd7af',
        'rgb': (255, 215, 175),
    },
    'navajowhite': {
        'code': 223,
        'hexval': 'ffd7af',
        'rgb': (255, 215, 175),
    },
    'navajowhite2': {
        'code': 180,
        'hexval': 'd7af87',
        'rgb': (215, 175, 135),
    },
    'navajowhite3': {
        'code': 101,
        'hexval': '87875f',
        'rgb': (135, 135, 95),
    },
    'navy': {
        'code': 18,
        'hexval': '000087',
        'rgb': (0, 0, 135),
    },
    'navyblue': {
        'code': 18,
        'hexval': '000087',
        'rgb': (0, 0, 135),
    },
    'oldlace': {
        'code': 230,
        'hexval': 'ffffd7',
        'rgb': (255, 255, 215),
    },
    'olivedrab': {
        'code': 64,
        'hexval': '5f8700',
        'rgb': (95, 135, 0),
    },
    'olivedrab2': {
        'code': 155,
        'hexval': 'afff5f',
        'rgb': (175, 255, 95),
    },
    'olivedrab3': {
        'code': 113,
        'hexval': '87d75f',
        'rgb': (135, 215, 95),
    },
    'olivedrab4': {
        'code': 64,
        'hexval': '5f8700',
        'rgb': (95, 135, 0),
    },
    'orange': {
        'code': 214,
        'hexval': 'ffaf00',
        'rgb': (255, 175, 0),
    },
    'orange2': {
        'code': 214,
        'hexval': 'ffaf00',
        'rgb': (255, 175, 0),
    },
    'orange3': {
        'code': 208,
        'hexval': 'ff8700',
        'rgb': (255, 135, 0),
    },
    'orange4': {
        'code': 172,
        'hexval': 'd78700',
        'rgb': (215, 135, 0),
    },
    'orange5': {
        'code': 94,
        'hexval': '875f00',
        'rgb': (135, 95, 0),
    },
    'orangered': {
        'code': 202,
        'hexval': 'ff5f00',
        'rgb': (255, 95, 0),
    },
    'orangered2': {
        'code': 166,
        'hexval': 'd75f00',
        'rgb': (215, 95, 0),
    },
    'orangered3': {
        'code': 88,
        'hexval': '870000',
        'rgb': (135, 0, 0),
    },
    'orchid': {
        'code': 170,
        'hexval': 'd75fd7',
        'rgb': (215, 95, 215),
    },
    'orchid2': {
        'code': 213,
        'hexval': 'ff87ff',
        'rgb': (255, 135, 255),
    },
    'orchid3': {
        'code': 212,
        'hexval': 'ff87d7',
        'rgb': (255, 135, 215),
    },
    'orchid4': {
        'code': 170,
        'hexval': 'd75fd7',
        'rgb': (215, 95, 215),
    },
    'orchid5': {
        'code': 96,
        'hexval': '875f87',
        'rgb': (135, 95, 135),
    },
    'palegoldenrod': {
        'code': 223,
        'hexval': 'ffd7af',
        'rgb': (255, 215, 175),
    },
    'palegreen': {
        'code': 120,
        'hexval': '87ff87',
        'rgb': (135, 255, 135),
    },
    'palegreen2': {
        'code': 114,
        'hexval': '87d787',
        'rgb': (135, 215, 135),
    },
    'palegreen3': {
        'code': 65,
        'hexval': '5f875f',
        'rgb': (95, 135, 95),
    },
    'paleturquoise': {
        'code': 159,
        'hexval': 'afffff',
        'rgb': (175, 255, 255),
    },
    'paleturquoise2': {
        'code': 116,
        'hexval': '87d7d7',
        'rgb': (135, 215, 215),
    },
    'paleturquoise3': {
        'code': 66,
        'hexval': '5f8787',
        'rgb': (95, 135, 135),
    },
    'palevioletred': {
        'code': 168,
        'hexval': 'd75f87',
        'rgb': (215, 95, 135),
    },
    'palevioletred2': {
        'code': 211,
        'hexval': 'ff87af',
        'rgb': (255, 135, 175),
    },
    'palevioletred3': {
        'code': 168,
        'hexval': 'd75f87',
        'rgb': (215, 95, 135),
    },
    'palevioletred4': {
        'code': 95,
        'hexval': '875f5f',
        'rgb': (135, 95, 95),
    },
    'papayawhip': {
        'code': 230,
        'hexval': 'ffffd7',
        'rgb': (255, 255, 215),
    },
    'peachpuff': {
        'code': 223,
        'hexval': 'ffd7af',
        'rgb': (255, 215, 175),
    },
    'peachpuff2': {
        'code': 223,
        'hexval': 'ffd7af',
        'rgb': (255, 215, 175),
    },
    'peachpuff3': {
        'code': 180,
        'hexval': 'd7af87',
        'rgb': (215, 175, 135),
    },
    'peachpuff4': {
        'code': 101,
        'hexval': '87875f',
        'rgb': (135, 135, 95),
    },
    'peru': {
        'code': 173,
        'hexval': 'd7875f',
        'rgb': (215, 135, 95),
    },
    'pink': {
        'code': 218,
        'hexval': 'ffafd7',
        'rgb': (255, 175, 215),
    },
    'pink2': {
        'code': 217,
        'hexval': 'ffafaf',
        'rgb': (255, 175, 175),
    },
    'pink3': {
        'code': 175,
        'hexval': 'd787af',
        'rgb': (215, 135, 175),
    },
    'pink4': {
        'code': 95,
        'hexval': '875f5f',
        'rgb': (135, 95, 95),
    },
    'plum': {
        'code': 182,
        'hexval': 'd7afd7',
        'rgb': (215, 175, 215),
    },
    'plum2': {
        'code': 219,
        'hexval': 'ffafff',
        'rgb': (255, 175, 255),
    },
    'plum3': {
        'code': 176,
        'hexval': 'd787d7',
        'rgb': (215, 135, 215),
    },
    'plum4': {
        'code': 96,
        'hexval': '875f87',
        'rgb': (135, 95, 135),
    },
    'powderblue': {
        'code': 152,
        'hexval': 'afd7d7',
        'rgb': (175, 215, 215),
    },
    'purple': {
        'code': 129,
        'hexval': 'af00ff',
        'rgb': (175, 0, 255),
    },
    'purple2': {
        'code': 135,
        'hexval': 'af5fff',
        'rgb': (175, 95, 255),
    },
    'purple3': {
        'code': 93,
        'hexval': '8700ff',
        'rgb': (135, 0, 255),
    },
    'purple4': {
        'code': 92,
        'hexval': '8700d7',
        'rgb': (135, 0, 215),
    },
    'purple5': {
        'code': 54,
        'hexval': '5f0087',
        'rgb': (95, 0, 135),
    },
    'red': {
        'code': 9,
        'hexval': 'ff0000',
        'rgb': (255, 0, 0),
    },
    'red2': {
        'code': 160,
        'hexval': 'd70000',
        'rgb': (215, 0, 0),
    },
    'red3': {
        'code': 88,
        'hexval': '870000',
        'rgb': (135, 0, 0),
    },
    'rosybrown': {
        'code': 138,
        'hexval': 'af8787',
        'rgb': (175, 135, 135),
    },
    'rosybrown2': {
        'code': 217,
        'hexval': 'ffafaf',
        'rgb': (255, 175, 175),
    },
    'rosybrown3': {
        'code': 181,
        'hexval': 'd7afaf',
        'rgb': (215, 175, 175),
    },
    'rosybrown4': {
        'code': 95,
        'hexval': '875f5f',
        'rgb': (135, 95, 95),
    },
    'royalblue': {
        'code': 62,
        'hexval': '5f5fd7',
        'rgb': (95, 95, 215),
    },
    'royalblue2': {
        'code': 69,
        'hexval': '5f87ff',
        'rgb': (95, 135, 255),
    },
    'royalblue3': {
        'code': 63,
        'hexval': '5f5fff',
        'rgb': (95, 95, 255),
    },
    'royalblue4': {
        'code': 62,
        'hexval': '5f5fd7',
        'rgb': (95, 95, 215),
    },
    'royalblue5': {
        'code': 24,
        'hexval': '005f87',
        'rgb': (0, 95, 135),
    },
    'saddlebrown': {
        'code': 94,
        'hexval': '875f00',
        'rgb': (135, 95, 0),
    },
    'salmon': {
        'code': 209,
        'hexval': 'ff875f',
        'rgb': (255, 135, 95),
    },
    'salmon2': {
        'code': 209,
        'hexval': 'ff875f',
        'rgb': (255, 135, 95),
    },
    'salmon3': {
        'code': 167,
        'hexval': 'd75f5f',
        'rgb': (215, 95, 95),
    },
    'salmon4': {
        'code': 95,
        'hexval': '875f5f',
        'rgb': (135, 95, 95),
    },
    'sandybrown': {
        'code': 215,
        'hexval': 'ffaf5f',
        'rgb': (255, 175, 95),
    },
    'seagreen': {
        'code': 29,
        'hexval': '00875f',
        'rgb': (0, 135, 95),
    },
    'seagreen2': {
        'code': 85,
        'hexval': '5fffaf',
        'rgb': (95, 255, 175),
    },
    'seagreen3': {
        'code': 84,
        'hexval': '5fff87',
        'rgb': (95, 255, 135),
    },
    'seagreen4': {
        'code': 78,
        'hexval': '5fd787',
        'rgb': (95, 215, 135),
    },
    'seagreen5': {
        'code': 29,
        'hexval': '00875f',
        'rgb': (0, 135, 95),
    },
    'seashell': {
        'code': 231,
        'hexval': 'ffffff',
        'rgb': (255, 255, 255),
    },
    'seashell2': {
        'code': 224,
        'hexval': 'ffd7d7',
        'rgb': (255, 215, 215),
    },
    'seashell3': {
        'code': 187,
        'hexval': 'd7d7af',
        'rgb': (215, 215, 175),
    },
    'seashell4': {
        'code': 102,
        'hexval': '878787',
        'rgb': (135, 135, 135),
    },
    'sienna': {
        'code': 130,
        'hexval': 'af5f00',
        'rgb': (175, 95, 0),
    },
    'sienna2': {
        'code': 209,
        'hexval': 'ff875f',
        'rgb': (255, 135, 95),
    },
    'sienna3': {
        'code': 167,
        'hexval': 'd75f5f',
        'rgb': (215, 95, 95),
    },
    'sienna4': {
        'code': 94,
        'hexval': '875f00',
        'rgb': (135, 95, 0),
    },
    'skyblue': {
        'code': 117,
        'hexval': '87d7ff',
        'rgb': (135, 215, 255),
    },
    'skyblue2': {
        'code': 111,
        'hexval': '87afff',
        'rgb': (135, 175, 255),
    },
    'skyblue3': {
        'code': 74,
        'hexval': '5fafd7',
        'rgb': (95, 175, 215),
    },
    'skyblue4': {
        'code': 60,
        'hexval': '5f5f87',
        'rgb': (95, 95, 135),
    },
    'slateblue': {
        'code': 62,
        'hexval': '5f5fd7',
        'rgb': (95, 95, 215),
    },
    'slateblue2': {
        'code': 99,
        'hexval': '875fff',
        'rgb': (135, 95, 255),
    },
    'slateblue3': {
        'code': 62,
        'hexval': '5f5fd7',
        'rgb': (95, 95, 215),
    },
    'slateblue4': {
        'code': 60,
        'hexval': '5f5f87',
        'rgb': (95, 95, 135),
    },
    'slategray': {
        'code': 66,
        'hexval': '5f8787',
        'rgb': (95, 135, 135),
    },
    'slategray2': {
        'code': 189,
        'hexval': 'd7d7ff',
        'rgb': (215, 215, 255),
    },
    'slategray3': {
        'code': 153,
        'hexval': 'afd7ff',
        'rgb': (175, 215, 255),
    },
    'slategray4': {
        'code': 146,
        'hexval': 'afafd7',
        'rgb': (175, 175, 215),
    },
    'slategray5': {
        'code': 66,
        'hexval': '5f8787',
        'rgb': (95, 135, 135),
    },
    'slategrey': {
        'code': 66,
        'hexval': '5f8787',
        'rgb': (95, 135, 135),
    },
    'snow': {
        'code': 231,
        'hexval': 'ffffff',
        'rgb': (255, 255, 255),
    },
    'snow2': {
        'code': 224,
        'hexval': 'ffd7d7',
        'rgb': (255, 215, 215),
    },
    'snow3': {
        'code': 188,
        'hexval': 'd7d7d7',
        'rgb': (215, 215, 215),
    },
    'snow4': {
        'code': 102,
        'hexval': '878787',
        'rgb': (135, 135, 135),
    },
    'springgreen': {
        'code': 48,
        'hexval': '00ff87',
        'rgb': (0, 255, 135),
    },
    'springgreen2': {
        'code': 48,
        'hexval': '00ff87',
        'rgb': (0, 255, 135),
    },
    'springgreen3': {
        'code': 41,
        'hexval': '00d75f',
        'rgb': (0, 215, 95),
    },
    'springgreen4': {
        'code': 29,
        'hexval': '00875f',
        'rgb': (0, 135, 95),
    },
    'steelblue': {
        'code': 67,
        'hexval': '5f87af',
        'rgb': (95, 135, 175),
    },
    'steelblue2': {
        'code': 75,
        'hexval': '5fafff',
        'rgb': (95, 175, 255),
    },
    'steelblue3': {
        'code': 68,
        'hexval': '5f87d7',
        'rgb': (95, 135, 215),
    },
    'steelblue4': {
        'code': 60,
        'hexval': '5f5f87',
        'rgb': (95, 95, 135),
    },
    'tan': {
        'code': 180,
        'hexval': 'd7af87',
        'rgb': (215, 175, 135),
    },
    'tan2': {
        'code': 215,
        'hexval': 'ffaf5f',
        'rgb': (255, 175, 95),
    },
    'tan3': {
        'code': 209,
        'hexval': 'ff875f',
        'rgb': (255, 135, 95),
    },
    'tan4': {
        'code': 173,
        'hexval': 'd7875f',
        'rgb': (215, 135, 95),
    },
    'tan5': {
        'code': 94,
        'hexval': '875f00',
        'rgb': (135, 95, 0),
    },
    'thistle': {
        'code': 182,
        'hexval': 'd7afd7',
        'rgb': (215, 175, 215),
    },
    'thistle2': {
        'code': 225,
        'hexval': 'ffd7ff',
        'rgb': (255, 215, 255),
    },
    'thistle3': {
        'code': 225,
        'hexval': 'ffd7ff',
        'rgb': (255, 215, 255),
    },
    'thistle4': {
        'code': 182,
        'hexval': 'd7afd7',
        'rgb': (215, 175, 215),
    },
    'thistle5': {
        'code': 102,
        'hexval': '878787',
        'rgb': (135, 135, 135),
    },
    'tomato': {
        'code': 203,
        'hexval': 'ff5f5f',
        'rgb': (255, 95, 95),
    },
    'tomato2': {
        'code': 167,
        'hexval': 'd75f5f',
        'rgb': (215, 95, 95),
    },
    'tomato3': {
        'code': 94,
        'hexval': '875f00',
        'rgb': (135, 95, 0),
    },
    'turquoise': {
        'code': 80,
        'hexval': '5fd7d7',
        'rgb': (95, 215, 215),
    },
    'turquoise2': {
        'code': 51,
        'hexval': '00ffff',
        'rgb': (0, 255, 255),
    },
    'turquoise3': {
        'code': 45,
        'hexval': '00d7ff',
        'rgb': (0, 215, 255),
    },
    'turquoise4': {
        'code': 44,
        'hexval': '00d7d7',
        'rgb': (0, 215, 215),
    },
    'turquoise5': {
        'code': 30,
        'hexval': '008787',
        'rgb': (0, 135, 135),
    },
    'violet': {
        'code': 213,
        'hexval': 'ff87ff',
        'rgb': (255, 135, 255),
    },
    'violetred': {
        'code': 162,
        'hexval': 'd70087',
        'rgb': (215, 0, 135),
    },
    'violetred2': {
        'code': 204,
        'hexval': 'ff5f87',
        'rgb': (255, 95, 135),
    },
    'violetred3': {
        'code': 168,
        'hexval': 'd75f87',
        'rgb': (215, 95, 135),
    },
    'violetred4': {
        'code': 89,
        'hexval': '87005f',
        'rgb': (135, 0, 95),
    },
    'wheat': {
        'code': 223,
        'hexval': 'ffd7af',
        'rgb': (255, 215, 175),
    },
    'wheat2': {
        'code': 223,
        'hexval': 'ffd7af',
        'rgb': (255, 215, 175),
    },
    'wheat3': {
        'code': 180,
        'hexval': 'd7af87',
        'rgb': (215, 175, 135),
    },
    'wheat4': {
        'code': 101,
        'hexval': '87875f',
        'rgb': (135, 135, 95),
    },
    'white': {
        'code': 231,
        'hexval': 'ffffff',
        'rgb': (255, 255, 255),
    },
    'whitesmoke': {
        'code': 231,
        'hexval': 'ffffff',
        'rgb': (255, 255, 255),
    },
    'yellow': {
        'code': 11,
        'hexval': 'ffff00',
        'rgb': (255, 255, 0),
    },
    'yellow2': {
        'code': 184,
        'hexval': 'd7d700',
        'rgb': (215, 215, 0),
    },
    'yellow3': {
        'code': 100,
        'hexval': '878700',
        'rgb': (135, 135, 0),
    },
    'yellowgreen': {
        'code': 113,
        'hexval': '87d75f',
        'rgb': (135, 215, 95),
    }
}
