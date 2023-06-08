import pyrtl
def prioritized_mux(selects, vals):
    """
    Returns the value in the first wire for which its select bit is 1

    :param [WireVector] selects: a list of WireVectors signaling whether
        a wire should be chosen
    :param [WireVector] vals: values to return when the corresponding select
        value is 1
    :return: WireVector

    If none of the items are high, the last val is returned
    """
    if len(selects) != len(vals):
        raise pyrtl.PyrtlError("Number of select and val signals must match")
    if len(vals) == 0:
        raise pyrtl.PyrtlError("Must have a signal to mux")
    if len(vals) == 1:
        return vals[0]
    else:
        half = len(vals) // 2
        return pyrtl.select(pyrtl.rtl_any(*selects[half:]),
                            truecase=prioritized_mux(selects[half:], vals[half:]),
                            falsecase=prioritized_mux(selects[:half], vals[:half]))