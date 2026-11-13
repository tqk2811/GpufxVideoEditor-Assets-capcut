// Linear wipe through alpha: a soft edge of width `feather` crosses the frame in `direction`,
// revealing the clip behind it. Progress is eased (in-out sine); 0 hides the clip, 1 shows it all.

@compute @workgroup_size(8, 8)
fn main(@builtin(global_invocation_id) id: vec3u) {
    if (!gpufx_in_bounds(id)) { return; }
    let c = textureLoad(src, vec2i(id.xy), 0);
    let p = clamp(params.progress, 0.0, 1.0);
    if (p >= 1.0) { gpufx_write(id, c); return; }
    let e = 0.5 - 0.5 * cos(3.14159265 * p);
    let uv = gpufx_uv(id);
    // Distance along the travel direction, 0 where the wipe starts and 1 where it ends.
    var d: f32;
    switch params.direction {
        case 1: { d = 1.0 - uv.x; }   // left
        case 2: { d = uv.y; }         // down
        case 3: { d = 1.0 - uv.y; }   // up
        default: { d = uv.x; }        // right
    }
    let f = max(params.feather, 1e-4);
    // The edge runs from -f to 1 so the frame is fully hidden at 0 and fully shown at 1.
    let edge = e * (1.0 + f);
    let a = 1.0 - smoothstep(edge - f, edge, d);
    gpufx_write(id, vec4f(c.rgb, c.a * a));
}
