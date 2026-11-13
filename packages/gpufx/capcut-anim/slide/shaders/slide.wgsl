// Slide inside the frame: the picture moves in from `direction` by `distance` frames while the clip
// itself stays put. Where the moved picture leaves the frame it is mirrored back in
// (1 - |(|uv| - 1)|), so no edge shows. The offset eases out (out cubic) and the motion blur
// follows its speed, so it is strongest at the start and gone at progress 1. One pass.

const MAX_TAPS: i32 = 32;

fn mirror(q: vec2f) -> vec2f {
    // Mirror repeat with a period of 2: ..., flipped, as is, flipped, ...
    let m = q - 2.0 * floor(q * 0.5);
    return 1.0 - abs(m - 1.0);
}

@compute @workgroup_size(8, 8)
fn main(@builtin(global_invocation_id) id: vec3u) {
    if (!gpufx_in_bounds(id)) { return; }
    let p = clamp(params.progress, 0.0, 1.0);
    if (p >= 1.0) {
        gpufx_write(id, textureLoad(src, vec2i(id.xy), 0));
        return;
    }
    // Unit vector the picture travels along.
    var dir: vec2f;
    switch params.direction {
        case 1: { dir = vec2f(-1.0, 0.0); }  // left
        case 2: { dir = vec2f(0.0, 1.0); }   // down
        case 3: { dir = vec2f(0.0, -1.0); }  // up
        default: { dir = vec2f(1.0, 0.0); }  // right
    }
    let r = 1.0 - p;
    // Picture offset: -distance at 0, 0 at 1. Speed is its derivative, 3 r^2 distance per unit.
    let offset = -dir * params.distance * r * r * r;
    let speed = 3.0 * r * r * params.distance;
    let uv = gpufx_uv(id) - offset;
    let span = dir * speed * params.motion_blur;
    let length_px = length(span * globals.size);
    if (length_px < 0.5) {
        gpufx_write(id, textureSampleLevel(src, smp, mirror(uv), 0.0));
        return;
    }
    let taps = clamp(i32(ceil(length_px * 0.5)), 2, MAX_TAPS);
    var sum = vec4f(0.0);
    for (var i = 0; i <= taps; i++) {
        let c = textureSampleLevel(src, smp, mirror(uv + span * (f32(i) / f32(taps) - 0.5)), 0.0);
        sum += vec4f(c.rgb * c.a, c.a);
    }
    sum /= f32(taps + 1);
    gpufx_write(id, vec4f(select(vec3f(0.0), sum.rgb / sum.a, sum.a > 1e-5), sum.a));
}
