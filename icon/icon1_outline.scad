include <BOSL2/std.scad>


r = 10;
a = 0.5;
inner_r = 8;
bar_thickness = 2;

res = 3600;


distorted_path = [
    for (i = [0:res-1]) let(
        t = i/res*360,
        x = cos(t),
        y = sin(t),
        scale = r + (t%180 >= 90 ? tan(t%90)*a : 0)
    ) [x * scale, y * scale]
];

rotate([0, 0, 22.5])
difference() {
    rotate([0, 0, 1/res*360])
    polygon(distorted_path);

    //square([tan(((res-1)/res*360)%90)*2*a, bar_thickness], center=true);
    square([1000, bar_thickness], center=true);
    circle(inner_r);
}