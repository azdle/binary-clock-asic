import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer, ClockCycles

# Asserts the reset pin for 1 millisecond, not taking any clocks
async def reset(dut):
    dut.RST.value = 1
    await ClockCycles(dut.CLK, 1)
    dut.RST.value = 0
    dut._log.debug("Reset complete")

# Create an indexable list of bits from a binstr
def bit_list(s):
    bits = list(s)
    bits.reverse()
    bits = list(map(lambda b: int(b), bits))
    return bits

@cocotb.test()
async def second_counter_counts_seconds(dut):
    dut._log.info("start")

    dut.PPS.value = 0;
    dut.HOURS_INIT.value = 0;

    clock = Clock(dut.CLK, 10, units="ms")
    cocotb.start_soon(clock.start())
    await reset(dut)

    # TODO: increase range, was 1001
    for i in range(0,100):
        await ClockCycles(dut.CLK, 1)
        assert dut.binary_clock.seconds.value.integer  == i % 60
        await ClockCycles(dut.CLK, 99)
        assert dut.binary_clock.seconds.value.integer  == i % 60

@cocotb.test()
async def verify_multiplexing_output(dut):
    dut._log.info("start")

    dut.PPS.value = 0;
    dut.HOURS_INIT.value = 0;

    clock = Clock(dut.CLK, 10, units="ms")
    cocotb.start_soon(clock.start())
    await reset(dut)

    #print(dut.binary_clock.hours_init.value.binstr)
    #print(dut.binary_clock.seconds.value.binstr)

    # check the output for every minute of an hour
    for current_minute in range(0, 60 + 1):
        # wait for wanted minute
        current_minute = current_minute % 60
        while True:
            await ClockCycles(dut.CLK, 100)
            if dut.binary_clock.minutes.value.integer == current_minute:
                break

        await ClockCycles(dut.CLK, 1)
        assert dut.binary_clock.minutes.value.integer == current_minute

        plex = [[0,0,0,0],
                [0,0,0,0],
                [0,0,0,0],
                [0,0,0,0]]

        for _ in range(0,4):
            pins = bit_list(dut.out.value.binstr)
            col = pins[0:4]
            row = pins[4:8]

            #print("pins", pins, col, row)

            assert sum(row) == 3

            row = row[0] == 0 and 0 or row[1] == 0 and 1 or row[2] == 0 and 2 or row[3] == 0 and 3

            for ci, cv in enumerate(col):
                #print(ci, cv)
                plex[row][ci] = cv

            await ClockCycles(dut.CLK, 1)

        #print("pat:", ("_" * 5) + ("h" * 5) + ("m" * 6))
        #print("inp:", dut.binary_clock.pixels.value.binstr)

        flat_plex = [str(pixel) for row in plex for pixel in row]
        flat_plex.reverse()
        str_plex = "".join(flat_plex)

        #print("out:", str_plex)

        assert str_plex == dut.binary_clock.pixels.value.binstr

@cocotb.test()
async def high_pps_takes_over_seconds(dut):
    dut._log.info("start")

    dut.PPS.value = 0;
    dut.HOURS_INIT.value = 0;

    clock = Clock(dut.CLK, 10, units="ms")
    cocotb.start_soon(clock.start())
    await reset(dut)

    # pull PPS high
    pps = dut.binary_clock.pps
    pps.value = 1

    # manually force and another reset while PPS is high
    dut.RST.value = 1
    await ClockCycles(dut.CLK, 2)
    dut.RST.value = 0
    await ClockCycles(dut.CLK, 2)

    for i in range(0,1000):
        #print("loop sec", i, dut.binary_clock.seconds.value.integer)
        await ClockCycles(dut.CLK, 100)
        assert dut.binary_clock.seconds.value.integer == 0

    for i in range(0,1000):
        await ClockCycles(dut.CLK, 3) # off of clock ms
        assert dut.binary_clock.seconds.value.integer == i % 60
        pps.value = 0
        await ClockCycles(dut.CLK, 3) # off of clock ms
        #print(i, dut.binary_clock.seconds.value.integer)
        assert dut.binary_clock.seconds.value.integer == i % 60
        pps.value = 1


@cocotb.test()
async def hours_initable(dut):
    dut._log.info("start")

    dut.PPS.value = 0;
    dut.HOURS_INIT.value = 0;

    clock = Clock(dut.CLK, 10, units="ms")
    cocotb.start_soon(clock.start())
    await reset(dut)

    hours = dut.binary_clock.hours
    hours_init = dut.binary_clock.hours_init
    rst = dut.binary_clock.rst

    #print(hours.value, hours_init.value, rst.value)

    # test each hour
    for i in range(0,24):
        hours_init.value = i
        await ClockCycles(dut.CLK, 1)

        rst.value = 1
        await ClockCycles(dut.CLK, 1)
        rst.value = 0
        await ClockCycles(dut.CLK, 1)

        #print(i, hours.value)
        assert hours.value == i
        await ClockCycles(dut.CLK, 1)
