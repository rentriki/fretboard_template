import json
import os

from dataclasses import dataclass

import cairo 

DPI = 72
BUFFER = int(DPI/4)
WIDTH = (8.5 * DPI) - (2 * BUFFER)
HEIGHT = (11 * DPI) - (2 * BUFFER)
MIN_X = BUFFER
MAX_X = WIDTH - BUFFER
MIN_Y = BUFFER
MAX_Y = HEIGHT - BUFFER
CENTER_X = (MAX_X - MIN_X) / 2

@dataclass
class FretboardConfig:
    edo: float
    fretboard_length: float
    scale_length: float

def read_config(infilename):
    with open(infilename) as infile:
        return FretboardConfig(**json.loads(infile.read()))

def in2cm(inches): 
    return 2.54 * inches

def fret_spacing(fret_num, config):
    return config.scale_length * (1 - 2**(-fret_num/config.edo))

def all_frets(config):
    i = 0
    fret = fret_spacing(i, config)
    while fret < config.fretboard_length:
        yield fret
        i += 1
        fret = fret_spacing(i, config)

def write_frets(context, frets, line_length):
    for i, fret in enumerate(frets):
        context.move_to(CENTER_X-(line_length/2), MIN_Y+fret*DPI)
        context.line_to(CENTER_X+(line_length/2), MIN_Y+fret*DPI)
        context.move_to(CENTER_X-(line_length/2)-(DPI/4), 
                        MIN_Y+(fret*DPI)+(DPI/4))
        context.show_text(str(i))

def write_boilerplate(config, context):

    # center line
    context.set_line_width(1)
    context.set_source_rgb(0, 0, 255)
    context.move_to(CENTER_X, MIN_Y)
    context.line_to(CENTER_X, MAX_Y)
    context.stroke()

    # one inch
    context.set_line_width(3)
    context.set_source_rgb(0, 255, 0)
    context.move_to(MIN_X, MIN_Y)
    context.line_to(MIN_X+(DPI/4), MIN_Y)
    context.move_to(MIN_X, MIN_Y+DPI)
    context.line_to(MIN_X+(DPI/4), MIN_Y+DPI)
    context.move_to(MIN_X, MIN_Y+(DPI/2))
    context.set_font_size(14)
    context.show_text(f'1 inch = {DPI}px')
    context.stroke()

    # config params
    context.set_source_rgb(0, 0, 0)
    context.move_to(MIN_X, MIN_Y+(DPI*1.5))
    context.show_text(f'{config.edo}EDO')
    context.move_to(MIN_X, MIN_Y+(DPI*1.75))
    context.show_text(f'{config.fretboard_length}" fretboard')
    context.move_to(MIN_X, MIN_Y+(DPI*2))
    context.show_text(f'{config.scale_length}" scale length')
    context.stroke()


def print_frets(config, outfilename):
    
    with cairo.SVGSurface(outfilename, WIDTH, HEIGHT) as surface:
        
        context = cairo.Context(surface)

        write_boilerplate(config, context)

        # 12edo frets
        context.set_line_width(1)
        context.set_source_rgb(50, 0, 0)
        context.set_font_size(26)
        twelve_edo_config = FretboardConfig(12, config.fretboard_length,
                                                config.scale_length)
        write_frets(context, all_frets(twelve_edo_config), DPI*2)
        context.stroke()
        
        # target frets
        context.set_line_width(2)
        context.set_source_rgb(0, 0, 0)
        target_frets = all_frets(config)
        write_frets(context, target_frets, DPI*3)
        context.stroke()
    
    print(f"Image saved as {outfilename}.")

if __name__ == '__main__':

    import argparse

    parser = argparse.ArgumentParser(description='Draw a fretboard.')
    parser.add_argument('config_filename')
    args = parser.parse_args()

    outfilename = os.path.basename(args.config_filename).split('.')[0] + '.svg'
    print_frets(read_config(args.config_filename), outfilename)