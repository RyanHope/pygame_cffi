""" XXX """

import pygame
from pygame._error import SDLError, unpack_rect
from pygame._sdl import sdl, locked, ffi, FillRect, BlitSurface
from pygame.rect import Rect, new_rect
from pygame.color import create_color


class Surface(object):
    """ Surface((width, height), flags=0, depth=0, masks=None) -> Surface
    Surface((width, height), flags=0, Surface) -> Surface

    pygame object for representing images
    """
    _c_surface = None

    def __init__(self, size, flags=0, depth=0, masks=None):
        w, h = unpack_rect(size)
        if isinstance(depth, Surface):
            surface = depth
            depth = 0
        else:
            surface = None

        if depth or masks:
            raise SDLError("XXX: Not implemented!")

        if surface is None:
            if sdl.SDL_GetVideoSurface():
                pix = sdl.SDL_GetVideoSurface().format
            elif sdl.SDL_WasInit(sdl.SDL_INIT_VIDEO):
                pix = sdl.SDL_GetVideoInfo().vfmt
            else:
                pix = ffi.new("SDL_PixelFormat*")
                pix.BitsPerPixel = 32
                pix.Amask = 0
                pix.Rmask = 0xff0000
                pix.Gmask = 0xFF00
                pix.Bmask = 0xFF
            self._c_surface = sdl.SDL_CreateRGBSurface(flags, w, h,
                                                       pix.BitsPerPixel,
                                                       pix.Rmask,
                                                       pix.Gmask,
                                                       pix.Bmask,
                                                       pix.Amask)
            if not self._c_surface:
                raise SDLError.from_sdl_error()

        else:
            raise NotImplementedError("xxx")

    def fill(self, color):
        c_color = create_color(color, self._format)
        sdlrect = new_rect(0, 0, self._w, self._h)
        with locked(self._c_surface):
            FillRect(self._c_surface, sdlrect, c_color)

    def blit(self, source, destrect, area=None, special_flags=0):
        assert area is None and special_flags == 0
        srcrect = new_rect(0, 0, source._w, source._h)
        if isinstance(destrect, tuple):
            destrect = new_rect(destrect[0], destrect[1], source._w, source._h)
        elif isinstance(destrect, Rect):
            destrect = destrect._sdlrect
        BlitSurface(source._c_surface, srcrect, self._c_surface, destrect)

    def get_format(self):
        return self._c_surface.format
    _format = property(get_format)

    def get_w(self):
        return self._c_surface.w
    _w = property(get_w)

    def get_h(self):
        return self._c_surface.h
    _h = property(get_h)

    @classmethod
    def _from_sdl_surface(cls, c_surface):
        surface = cls.__new__(cls)
        surface._c_surface = c_surface
        return surface

    def get_rect(self):
        return Rect(0, 0, self._w, self._h)

    def set_at(self, pos, color):
        x, y = pos
        c_color = create_color(color, self._format)
        with locked(self._c_surface):
            bpp = self._format.BytesPerPixel
            if bpp == 1:
                pixels = ffi.cast("uint8_t*", self._c_surface.pixels)
                pixels[y * self._c_surface.pitch // bpp + x] = c_color
            elif bpp == 2:
                pixels = ffi.cast("uint16_t*", self._c_surface.pixels)
                pixels[y * self._c_surface.pitch // bpp + x] = c_color
            elif bpp == 3:
                pixels = ffi.cast("uint8_t*", self._c_surface.pixels)
                raise RuntimeError("Not implemented")
            elif bpp == 4:
                pixels = ffi.cast("uint32_t*", self._c_surface.pixels)
                pixels[y * self._c_surface.pitch // bpp + x] = c_color
            else:
                raise RuntimeError("Unknown pixel format")


        
