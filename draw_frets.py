import json
import math
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
    width1: float
    width2: float

def read_config(infilename):
    with open(infilename) as infile:
        return FretboardConfig(**json.loads(infile.read()))

def in2cm(inches): 
    return 2.54 * inches

def fret_spacing(fret_num, config):
    return config.scale_length * (1 - 2**(-fret_num/config.edo))

def all_frets(config):
    # in inches
    i = 0
    fret = fret_spacing(i, config)
    while fret < config.fretboard_length:
        yield fret
        i += 1
        fret = fret_spacing(i, config)

def sine_wave(fret_pos, config):
    x = math.radians(360*fret_pos/(config.scale_length/2))
    return math.sin(x)

def fretboard_width(fret_pos, config):
    return config.width1 + ((config.width2-config.width1) * 
                           (fret_pos/config.fretboard_length))

def x_pos(fret_pos, config):
    return sine_wave(fret_pos, config) * (fretboard_width(fret_pos, config)/2)

def all_frets_with_sine_wave(config):
    # in inches
    i = 0
    fret = fret_spacing(i, config)
    x = x_pos(fret, config)
    while fret < config.fretboard_length:
        yield fret, x
        i += 1
        fret = fret_spacing(i, config)
        x = x_pos(fret, config)

def write_frets(context, frets, line_length):
    for (fret_num, (y, x)) in frets:
        context.move_to(CENTER_X-(line_length/2), MIN_Y+y*DPI)
        context.line_to(CENTER_X+(line_length/2), MIN_Y+y*DPI)
        context.move_to(CENTER_X+(x*DPI), MIN_Y+y*DPI-2)
        context.line_to(CENTER_X+(x*DPI), MIN_Y+y*DPI+2)
        context.move_to(CENTER_X-(line_length/2)-(DPI/4), 
                        MIN_Y+(y*DPI)+(DPI/4))
        context.show_text(str(fret_num))

def paginate_frets(target, baseline):
    target, baseline = map(lambda x: list(enumerate(x)), [target, baseline])
    while len(target) > 1:
        i, j = 0, 0
        while (i < len(target)) and (target[i][1][0]*DPI < MAX_Y):
            i += 1
        while (j < len(baseline)) and baseline[j][1][0]*DPI < MAX_Y:
            j += 1
        yield (target[:i], baseline[:j])
        snip = target[i-1][1][0]
        target = [[fret_num, (y-snip, x)] for fret_num, (y, x) in target[i-1:]]
        baseline = [[fret_num, (y-snip, x)] for fret_num, (y, x) in baseline 
                                            if y-snip > 0]

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


def print_frets(config, outdir):
    
    twelve_edo_config = FretboardConfig(12, config.fretboard_length,
                                            config.scale_length,
                                            config.width1,
                                            config.width2)
    twedo_frets = all_frets_with_sine_wave(twelve_edo_config)
    target_frets = all_frets_with_sine_wave(config)
    
    for (page_num, (target, baseline)) in enumerate(paginate_frets(target_frets, 
                                                    twedo_frets), start=1):

        outfilename = f"{outdir}/page{page_num}.svg"
        
        with cairo.SVGSurface(outfilename, WIDTH, HEIGHT) as surface:
            
            context = cairo.Context(surface)
            write_boilerplate(config, context)
            context.set_font_size(26)

            # 12edo frets
            context.set_line_width(1)
            context.set_source_rgb(50, 0, 0)
            write_frets(context, baseline, DPI*2)
            context.stroke()
            
            # target frets
            context.set_line_width(2)
            context.set_source_rgb(0, 0, 0)
            write_frets(context, target, DPI*3)
            context.stroke()
    
    print(f"Images saved in ./{outdir}.")

if __name__ == '__main__':

    import argparse, os, shutil

    parser = argparse.ArgumentParser(description='Draw a fretboard.')
    parser.add_argument('config_filename')
    args = parser.parse_args()

    outdir = os.path.basename(args.config_filename).split('.')[0]
    config = read_config(args.config_filename)

    shutil.rmtree(outdir, ignore_errors=True)
    os.mkdir(outdir)

    print_frets(config, outdir)