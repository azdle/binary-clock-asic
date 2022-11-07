import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer, ClockCycles

# Asserts the reset pin for 1 millisecond, not taking any clocks
async def reset(reset_wire):
    reset_wire.value = 1
    await Timer(1, units="ms")
    reset_wire.value = 0
    reset_wire._log.debug("Reset complete")

# Create an indexable list of bits from a binstr
def bit_list(s):
    bits = list(s)
    bits.reverse()
    return bits

@cocotb.test()
async def second_counter_counts_seconds(dut):
    dut._log.info("start")

    clock = Clock(dut.CLK, 10, units="ms")
    cocotb.start_soon(clock.start())
    await reset(dut.RST)

    # TODO: increase range, was 1001
    for i in range(0,100):
        await ClockCycles(dut.CLK, 1)
        assert dut.binary_clock.seconds.value.integer  == i % 60
        await ClockCycles(dut.CLK, 99)
        assert dut.binary_clock.seconds.value.integer  == i % 60

@cocotb.test()
async def verify_charlieplexing_output(dut):
    dut._log.info("start")

    clock = Clock(dut.CLK, 10, units="ms")
    cocotb.start_soon(clock.start())
    await reset(dut.RST)

    # check the output for every second of a minute
    for current_second in range(0, 60 + 1):
        # wait for second
        current_second = current_second % 60
        while True:
            await ClockCycles(dut.CLK, 1)
            if dut.binary_clock.seconds.value.integer == current_second:
                break

        await ClockCycles(dut.CLK, 1)
        assert dut.binary_clock.seconds.value.integer == current_second

        plex = [[0,0,0,0,0],
                [0,0,0,0,0],
                [0,0,0,0,0],
                [0,0,0,0,0],
                [0,0,0,0,0],
                [0,0,0,0,0]]

        for _ in range(0,6):
            row = dut.binary_clock.disp.row.value.integer
            pins = bit_list(dut.out.value.binstr)

            #print("row", row, pins)

            diff = 0

            for pin, state in enumerate(pins):
                #print(row, pin, state)
                if pin >= 6:
                    break
                elif pin == row:
                    assert state == '1'
                    diff = -1
                else:
                    plex[row][pin + diff] = 0 if state == 'z' else 1

            await ClockCycles(dut.CLK, 1)

        #print("pat:", ("_" * 13) + ("h" * 5) + ("m" * 6) + ("s" * 6))
        #print("inp:", dut.binary_clock.pixels.value.binstr)

        flat_plex = [str(pixel) for row in plex for pixel in row]
        flat_plex.reverse()
        str_plex = "".join(flat_plex)

        #print("out:", str_plex)

        assert str_plex == dut.binary_clock.pixels.value.binstr
