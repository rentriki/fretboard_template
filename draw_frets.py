import cairo 

DPI = 150
EDO = 19
FRETBOARD_LENGTH = 18 + (3/8)
SCALE_LENGTH = 25

def in2cm(inches): 
    return 2.54 * inches

def fret_spacing(fret_num, scale_len=SCALE_LENGTH, tet_num=EDO):
    return scale_len * (1 - 2**(-fret_num/tet_num))

def all_frets(fretboard_len=FRETBOARD_LENGTH, **kwargs):
    i = 0
    fret = fret_spacing(i, **kwargs)
    while fret < fretboard_len:
        yield fret
        i += 1
        fret = fret_spacing(i, **kwargs)

def write_frets(context, frets, line_len=DPI):
    for i, fret in enumerate(frets):
        context.move_to(0, int(fret*DPI))
        context.line_to(line_len, int(fret*DPI))
        context.move_to(line_len+20, int(fret*DPI)+20)
        context.show_text(str(i))

def print_frets(fretboard_len=FRETBOARD_LENGTH, 
                scale_len=SCALE_LENGTH, tet_num=EDO,
                outfilename="19edo.svg", 
                width=8.5*DPI, height=FRETBOARD_LENGTH*DPI):
    
    with cairo.SVGSurface(outfilename, width, height) as surface:
        
        context = cairo.Context(surface)
        context.set_font_size(30)

        context.set_line_width(3)
        context.set_source_rgb(50, 0, 0)
        twelve_edo_frets = all_frets(fretboard_len=fretboard_len,
                                     scale_len=scale_len,
                                     tet_num=12)
        write_frets(context, twelve_edo_frets, line_len=DPI//2)
        context.stroke()

        context.set_line_width(5)
        context.set_source_rgb(0, 0, 0)
        target_frets = all_frets(fretboard_len=fretboard_len,
                                 scale_len=scale_len,
                                 tet_num=tet_num)
        write_frets(context, target_frets, line_len=DPI)
        context.stroke()
    
    print(f"Image saved as {outfilename}.")

if __name__ == '__main__':

    print_frets()