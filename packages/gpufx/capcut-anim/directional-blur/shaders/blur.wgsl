// Directional blur that clears as the animation plays: at progress 0 the clip is smeared along
// `angle` by `strength`, and the smear eases out (out cubic) to the untouched clip at 1.
// One pass: taps along the line, weighted in premultiplied alpha so transparent edges stay clean.

const MAX_TAPS: i32 = 48;

@compute @workgroup_size(8, 8)
fn main(@builtin(global_invocation_id) id: vec3u) {
    if (!gpufx_in_bounds(id)) { return; }
    let p = clamp(params.progress, 0.0, 1.0);
    let amount = params.strength * pow(1.0 - p, 3.0);
    // Blur length in pixels, measured against the longer side so it looks the same in any shape.
    let dims = globals.size;
    let length_px = amount * max(dims.x, dims.y);
    if (length_px < 0.5) {
        gpufx_write(id, textureLoad(src, vec2i(id.xy), 0));
        return;
    }
    let a = radians(params.angle);
    let dir = vec2f(cos(a), sin(a)) * length_px / dims;
    // About one tap every two pixels; bilinear reads fill the gaps.
    let taps = clamp(i32(ceil(length_px * 0.5)), 2, MAX_TAPS);
    let uv = gpufx_uv(id);
    var sum = vec4f(0.0);
    for (var i = 0; i <= taps; i++) {
        let t = f32(i) / f32(taps) - 0.5;
        let c = textureSampleLevel(src, smp, uv + dir * t, 0.0);
        sum += vec4f(c.rgb * c.a, c.a);
    }
    sum /= f32(taps + 1);
    let rgb = select(vec3f(0.0), sum.rgb / sum.a, sum.a > 1e-5);
    gpufx_write(id, vec4f(rgb, sum.a));
}
