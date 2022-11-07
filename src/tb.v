`default_nettype none
`timescale 1ms/1ms

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

    wire [7:0] inputs = {6'b0, RST, CLK};

    azdle_binary_clock binary_clock (
        .opins (out),
        .rst(RST),
        .clk(CLK)
    );

endmodule
