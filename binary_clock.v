module binary_clock(
  input rst,
  input clk,
  output reg[7:0] opins
);
  wire state;

  wire d_tick; // ticks once per day
  wire [4:0] hours;
  wire h_tick; // ticks once per hour
  wire [5:0] minutes;
  wire m_tick; // ticks once per minute
  wire [5:0] seconds;
  wire s_tick; // ticks once per second
  wire [6:0] centiseconds;

  wire [29:0] pixels;

  wire [5:0] disp_pins;

  clock c(.rst, .clk, .d_tick, .h_tick, .m_tick, .s_tick,
                               .hours, .minutes, .seconds, .centiseconds);
  display disp(.rst, .clk, .pins(disp_pins), .pixels);

  assign pixels = { 13'b0, hours, minutes, seconds };
  assign opins = rst ? 0 : {1'b0, 1'b0, disp_pins};
endmodule

// zero or high-z (maps 1 -> 0, 0 -> Z)
function zz;
  input pixel;

  zz = pixel ? 0 : 78'bZ;
endfunction

module display (
  input rst,
  input clk,
  input [6-1:0][6-2:0] pixels, // [row][column]
  output reg [6-1:0] pins
);

  wire tick;
  wire [2:0] row;

  overflow_counter #(.bits(3))
    row_cycle(.rst(rst), .clk(clk), .cmp(3'd6), .cnt(row), .tick(tick));

  always @(posedge clk)
    if (rst)
      pins <= 0;
    else
      case (row)
        0: pins = { zz(pixels[0][4]), zz(pixels[0][3]), zz(pixels[0][2]), zz(pixels[0][1]), zz(pixels[0][0]), 1'b1 };
        1: pins = { zz(pixels[1][4]), zz(pixels[1][3]), zz(pixels[1][2]), zz(pixels[1][1]), 1'b1, zz(pixels[1][0]) };
        2: pins = { zz(pixels[2][4]), zz(pixels[2][3]), zz(pixels[2][2]), 1'b1, zz(pixels[2][1]), zz(pixels[2][0]) };
        3: pins = { zz(pixels[3][4]), zz(pixels[3][3]), 1'b1, zz(pixels[3][2]), zz(pixels[3][1]), zz(pixels[3][0]) };
        4: pins = { zz(pixels[4][4]), 1'b1, zz(pixels[4][3]), zz(pixels[4][2]), zz(pixels[4][1]), zz(pixels[4][0]) };
        5: pins = { 1'b1, zz(pixels[5][4]), zz(pixels[5][3]), zz(pixels[5][2]), zz(pixels[5][1]), zz(pixels[5][0]) };
      endcase
endmodule

module clock(
  input rst,
  input clk,
  output d_tick, // ticks once per day
  output [4:0] hours,
  output h_tick, // ticks once per hour
  output [5:0] minutes,
  output m_tick, // ticks once per minute
  output [5:0] seconds,
  output s_tick, // ticks once per second
  output [6:0] centiseconds
);

  overflow_counter #(.bits(5))
    h_cnt(.rst(rst), .clk(h_tick), .cmp(5'd24), .cnt(hours), .tick(d_tick));
  overflow_counter #(.bits(6))
    m_cnt(.rst(rst), .clk(m_tick), .cmp(6'd60), .cnt(minutes), .tick(h_tick));
  overflow_counter #(.bits(6))
    s_cnt(.rst(rst), .clk(s_tick), .cmp(6'd60), .cnt(seconds), .tick(m_tick));
  overflow_counter #(.bits(7))
    ms_cnt(.rst(rst), .clk(clk), .cmp(7'd100), .cnt(centiseconds), .tick(s_tick));
endmodule

module overflow_counter #(parameter bits = 8) (
  input rst,
  input clk,
  input [bits-1:0] cmp, // even numbers only, rolls over instead of reaching this number
  output reg [bits-1:0] cnt,
  output reg tick
);

  always @(posedge clk or posedge rst)
    begin
      if (rst) begin
        cnt <= 0;
        tick <= 1;
      end else
        // wrap to zero instead of reaching cmp
        if (cnt == cmp-1) begin
          cnt <= 0;
          tick <= 1;
        end
        else begin
          cnt <= cnt + 1;

          // unset tick halfway through, odd values for cmp result in unbalanced tick segments
          if (cnt == (cmp/2)-1)
            tick <= 0;
        end
    end
endmodule
