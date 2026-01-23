circle_radius = 10;
circle_thickness = 2;
outer_circle_scale = 2/3;

res = 210;
$fn=res;
 
intersection() {
    union() {
        difference() {
            circle(circle_radius);
            circle(circle_radius-circle_thickness);

            translate([-(circle_radius), 0]) 
            circle(circle_radius*outer_circle_scale);

            translate([(circle_radius), 0])
            circle(circle_radius*outer_circle_scale);
        }

        translate([-(circle_radius), 0]) 
        difference() {
            circle(circle_radius*outer_circle_scale);
            circle(circle_radius*outer_circle_scale-circle_thickness);
        }

        translate([(circle_radius), 0])
        difference() {
            circle(circle_radius*outer_circle_scale);
            circle(circle_radius*outer_circle_scale-circle_thickness);
        }

        difference() {
            circle(circle_radius-(circle_radius*outer_circle_scale-circle_thickness));
            circle(circle_radius-(circle_radius*outer_circle_scale-circle_thickness)-circle_thickness);
        }
    }

    circle(circle_radius);
}