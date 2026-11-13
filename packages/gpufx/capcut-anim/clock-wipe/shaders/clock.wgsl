// Clock wipe through alpha: a hand sweeps around `center` from `start_angle` (degrees, 0 = twelve
// o'clock) and reveals the clip behind it, with a soft edge of `feather` turns. Progress is eased
// (in-out sine); 0 hides the clip, 1 shows it all.

@compute @workgroup_size(8, 8)
fn main(@builtin(global_invocation_id) id: vec3u) {
    if (!gpufx_in_bounds(id)) { return; }
    let c = textureLoad(src, vec2i(id.xy), 0);
    let p = clamp(params.progress, 0.0, 1.0);
    if (p >= 1.0) { gpufx_write(id, c); return; }
    let e = 0.5 - 0.5 * cos(3.14159265 * p);
    // Offset from the centre in pixels, so the sweep is round on any frame shape; y points down.
    let v = (gpufx_uv(id) - params.center) * globals.size;
    // Clockwise angle from twelve o'clock, in turns 0..1.
    var turn = atan2(v.x, -v.y) / 6.28318531 - params.start_angle / 360.0;
    if (params.clockwise == 0u) { turn = -turn; }
    turn = fract(turn);
    let f = max(params.feather, 1e-4);
    let edge = e * (1.0 + f);
    let a = 1.0 - smoothstep(edge - f, edge, turn);
    gpufx_write(id, vec4f(c.rgb, c.a * a));
}
