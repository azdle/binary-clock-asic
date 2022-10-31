module binary_clock(
  input rst,
  input clk,
  output reg[7:0] opins
);
  wire state;
  
  wire d_tick; // ticks once per day
  wire reg [4:0] hours;
  wire h_tick; // ticks once per hour
  wire reg [5:0] minutes;
  wire m_tick; // ticks once per minute
  wire reg [5:0] seconds;
  wire s_tick; // ticks once per second
  wire reg [6:0] miliseconds;
  
  wire reg [7:0] display;
  wire reg [7:0] display0;
  wire reg [7:0] display1;
  wire reg [7:0] display2;
  
  wire reg [1:0] current_display;
  
  clock c(.rst, .clk, .d_tick, .h_tick, .m_tick, .s_tick, .hours, .minutes, .seconds, .miliseconds);

  assign opins = rst ? 0 : display;
  
  assign display0 = rst ? 0 : {3'd0, hours};
  assign display1 = rst ? 0 : {2'd0, minutes};
  assign display2 = rst ? 0 : {2'd0, seconds};
  
  always @(edge clk)
    case(current_display)
      0: begin current_display <= 1; display <= display1; end
      1: begin current_display <= 2; display <= display2; end
      2: begin current_display <= 0; display <= display0; end
    endcase
endmodule

module clock(
  input rst,
  input clk,
  output d_tick, // ticks once per day
  output reg [4:0] hours,
  output h_tick, // ticks once per hour
  output reg [5:0] minutes,
  output m_tick, // ticks once per minute
  output reg [5:0] seconds,
  output s_tick, // ticks once per second
  output reg [6:0] miliseconds // 
);
  
  overflow_counter #(.bits(5)) h_cnt(.rst(rst), .clk(h_tick), .cmp(24), .cnt(hours), .tick(d_tick));
  overflow_counter #(.bits(6)) m_cnt(.rst(rst), .clk(m_tick), .cmp(59), .cnt(minutes), .tick(h_tick));
  overflow_counter #(.bits(6)) s_cnt(.rst(rst), .clk(s_tick), .cmp(59), .cnt(seconds), .tick(m_tick));
  overflow_counter #(.bits(7)) ms_cnt(.rst(rst), .clk(clk), .cmp(99), .cnt(miliseconds), .tick(s_tick));
endmodule

module overflow_counter #(parameter bits = 8) (
  input rst,
  input clk,
  input reg [bits-1:0] cmp,
  output reg [bits-1:0] cnt,
  output tick
);
  
  always @(edge clk or edge rst)
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
