// Zoom blur: the clip starts scaled by `scale` around `center` and smeared radially by `strength`,
// and both ease out (out cubic) to the untouched clip at progress 1. One pass: taps along the ray
// from the centre, in premultiplied alpha. Outside the scaled clip is transparent.

const MAX_TAPS: i32 = 40;

fn read(q: vec2f) -> vec4f {
    if (any(q < vec2f(0.0)) || any(q > vec2f(1.0))) { return vec4f(0.0); }
    let c = textureSampleLevel(src, smp, q, 0.0);
    return vec4f(c.rgb * c.a, c.a);
}

@compute @workgroup_size(8, 8)
fn main(@builtin(global_invocation_id) id: vec3u) {
    if (!gpufx_in_bounds(id)) { return; }
    let p = clamp(params.progress, 0.0, 1.0);
    if (p >= 1.0) {
        gpufx_write(id, textureLoad(src, vec2i(id.xy), 0));
        return;
    }
    let k = pow(1.0 - p, 3.0);
    let s = max(mix(1.0, params.scale, k), 0.01);
    let blur = params.strength * k;
    let c = params.center;
    // Source point of this pixel once the zoom is undone.
    let q = c + (gpufx_uv(id) - c) / s;
    // Radial smear: sample from q towards the centre over `blur` of its distance.
    let span = (q - c) * blur;
    let length_px = length(span * globals.size);
    if (length_px < 0.5) {
        let v = read(q);
        gpufx_write(id, vec4f(select(vec3f(0.0), v.rgb / v.a, v.a > 1e-5), v.a));
        return;
    }
    let taps = clamp(i32(ceil(length_px * 0.5)), 2, MAX_TAPS);
    var sum = vec4f(0.0);
    for (var i = 0; i <= taps; i++) {
        sum += read(q - span * (f32(i) / f32(taps)));
    }
    sum /= f32(taps + 1);
    gpufx_write(id, vec4f(select(vec3f(0.0), sum.rgb / sum.a, sum.a > 1e-5), sum.a));
}
