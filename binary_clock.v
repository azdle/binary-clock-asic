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
  wire [6:0] miliseconds;

  wire [5:0] disp_pins;

  clock c(.rst, .clk, .d_tick, .h_tick, .m_tick, .s_tick,
                               .hours, .minutes, .seconds, .miliseconds);
  display disp(.rst, .clk, .pins(disp_pins), .pixels({30'b0}));

  assign opins = rst ? 0 : {1'b0, 1'b0, disp_pins};
endmodule

module display (
  input rst,
  input clk,
  input [6-1:0][6-2:0] pixels, // [row][column]
  output reg [6-1:0] pins
);

  wire tick;
  wire [2:0] row;

  assign display = current_display == 0 ? display0 :
	           current_display == 1 ? display1 :
		   current_display == 3 ? display2 :
		   display0;

  always @(posedge clk or negedge clk)
    case(current_display)
      0: current_display <= 1;
      1: current_display <= 2;
      2: current_display <= 0;
      3: current_display <= 0;
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
  output [6:0] miliseconds
);

  overflow_counter #(.bits(5))
    h_cnt(.rst(rst), .clk(h_tick), .cmp(5'd24), .cnt(hours), .tick(d_tick));
  overflow_counter #(.bits(6))
    m_cnt(.rst(rst), .clk(m_tick), .cmp(6'd60), .cnt(minutes), .tick(h_tick));
  overflow_counter #(.bits(6))
    s_cnt(.rst(rst), .clk(s_tick), .cmp(6'd60), .cnt(seconds), .tick(m_tick));
  overflow_counter #(.bits(7))
    ms_cnt(.rst(rst), .clk(clk), .cmp(7'd100), .cnt(miliseconds), .tick(s_tick));
endmodule

module overflow_counter #(parameter bits = 8) (
  input rst,
  input clk,
  input [bits-1:0] cmp,
  output reg [bits-1:0] cnt,
  output reg tick
);

  always @(posedge clk or negedge clk or posedge rst or negedge clk)
    begin
      if (rst)
        begin
        cnt <= 0;
        tick <= 1;
        end
      else
        begin
          // halfway through cycle (possibly on half-clock), reset tick
          if ({cnt[bits-2:0], ~clk} == cmp)
            tick <= 0;

          // wrap to zero when we reach cmp
          if (cnt == cmp)
            begin
              cnt <= 0;
              tick <= 1;
            end
          // inc count, full-clock only
          else if (clk)
            cnt <= cnt + 1;
        end
    end
endmodule
