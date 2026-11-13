# Backlog

CapCut animations not recreated yet, by what they need. Counts come from the reference set
(650 animations: Texts 601, Stickers 24, Videos 25).

## [Vừa] Class A text animations driven by keyframe files

About 87 text animations keep their motion in `studioAnim.lsanim` keyframe files. Only 19 of those
files are plain JSON; the other 68 (for example Neon Flicker, Stretchy Bouncy, Steady Pulse,
Pendulum Clock, Leftward/Rightward Pirouette, Rise Up, Spin Slam, Turbo Spin-In, Drop & Rebound)
are encrypted and were not read, so they can only be recreated by watching them in CapCut.

Of the 19 readable files, Small Jumps, Excited Jumps, Steady Hops and Small Bounces share the same
keyframes and became `bob` in `capcut-anim-text`; their differences live in the encrypted project
file. The rest are per character after all and belong to class B: Slide & Rise, Sign Flicker, Flip
Down, Sliding Drop and Cheeky Bounce animate the range selector offset, Ocean Bounce and Jittery
Assembly stagger with `as`/`ae` selectors, and Cheerful Lineup, Pinball Shots, Random Order, Giddy
Rainbow, Domino Out, Grainy Magic, Flip Fade and Balloons Pop run a selector script
(`lumi_animation.jsdat`).

## [Thấp] Class B: per character

44 animations (Texts 43, Stickers 1) animate each letter, word or line with a stagger (Type 1/2/3,
Squeeze, Slingshot, Boing, Tremble, Wave, Random Bounce, Float). They need per-glyph rendering and a
range selector in the editor.

## [Thấp] Class C: shader

About 300 animations (all 25 video animations, most text ones) need a shader. The first batch is in
`packages/gpufx/capcut-anim/`: directional blur, zoom blur, wipes, clock wipe, slide inside the
frame. They are used by the items of `capcut-anim-video` (blur, zoom blur, wipe, clock wipe and
slide, in and out).

## [Vừa] Wipe and slide in the other three directions

The `direction` param of `wipe` and `slide` is an enum, and the editor's item `effect` accepts no
enum param, so `capcut-anim-video` only has them going right. Left, up and down need either enum
support in the item `effect` or numeric direction params in the shader packages.

## [Thấp] Class C shader batch 2

Glitch, chromatic aberration, color flicker and a dissolve through procedural noise, as gpufx
packages with one input and a `progress` param like the first batch.

## [Thấp] Class D: media

About 180 animations use images, videos or fonts (noise or mask textures, overlays, a bundled font).
Masks and noise can be made procedurally; the rest stays out of scope, since no CapCut media may be
included.
