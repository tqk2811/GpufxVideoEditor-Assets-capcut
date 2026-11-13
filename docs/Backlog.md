# Backlog

CapCut animations not recreated yet, by what they need. Counts come from the reference set
(650 animations: Texts 601, Stickers 24, Videos 25).

## [Vá»«a] Class A text animations driven by keyframe files

About 87 text animations move the whole clip with alpha, scale, position and rotation only, but
their motion is stored as keyframe data rather than simple tweens (for example Neon Flicker, Sign
Flicker, Stretchy Bouncy, Steady Pulse, Pendulum Clock, Leftward/Rightward Pirouette, Rise Up,
Spin Slam, Turbo Spin-In/Out, Drop & Rebound). They fit the current curve format; each needs its
keyframes read and rewritten by hand.

## [Tháº¥p] Class B: per character

44 animations (Texts 43, Stickers 1) animate each letter, word or line with a stagger (Type 1/2/3,
Squeeze, Slingshot, Boing, Tremble, Wave, Random Bounce, Float). They need per-glyph rendering and a
range selector in the editor.

## [Tháº¥p] Class C: shader

About 300 animations (all 25 video animations, most text ones) need a shader: directional or zoom
blur, wipes, clock wipe, glitch, slide inside the frame with motion blur. They need gpufx effect
packages driven by a `progress` parameter.

## [Tháº¥p] Class D: media

About 180 animations use images, videos or fonts (noise or mask textures, overlays, a bundled font).
Masks and noise can be made procedurally; the rest stays out of scope, since no CapCut media may be
included.
