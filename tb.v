`default_nettype none
`timescale 1ns/1ps

module tb (
  input CLK,
  input RST,
  output [7:0] out
);

    initial begin
        $dumpfile ("tb.vcd");
        $dumpvars (0, tb);
        #1;
    end

    wire [7:0] clockout;

    wire [7:0] inputs = {6'b0, RST, CLK};
    wire [7:0] outputs = clockout;

    binary_clock binary_clock (
        .opins (clockout),
        .rst(RST),
        .clk(CLK)
    );

endmodule
