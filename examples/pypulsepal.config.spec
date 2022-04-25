serial_port = string(default="")
baudrate = integer(default=115200)
cycle_frequency = integer(default=20000)
nr_output_channels = integer(default=4)
nr_trigger_channels = integer(default=2)
firmware_opcode = integer(default=213)

# https://sites.google.com/site/pulsepalwiki/matlab-gnu-octave/functions/programpulsepalparam

custom_pulse_train_1 = float_list(default=list())
custom_pulse_train_2 = float_list(default=list())

[channels]
    [[ __many__]]
        # channel ID
        channel = integer(default=0, min=0, max=3)

        # channel params
        isBiphasic = boolean(default=False)
        phase1Voltage = float(default=5, min=-10, max=10)
        phase2Voltage = float(default=-5, min=-10, max=10)

        phase1Duration = float(default=0.001, min=0.001, max=3600)
        interPhaseInterval = float(default=0.001)
        phase2Duration = float(default=0.001)
        interPulseInterval = float(default=0.01)
        burstDuration = float(default=0)

        interBurstInterval = float(default=0)
        pulseTrainDuration = float(default=1)
        pulseTrainDelay = float(default=0)

        linkTriggerChannel1 = integer(default=1, min=0, max=1)
        linkTriggerChannel2 = integer(default=0, min=0, max=1)
        customTrainID = integer(default=0, min=0, max=2)
        customTrainTarget = integer(default=0, min=0, max=1)
        restingVoltage = integer(default=0, min=-10, max=10)


[triggers]
    [[__many__]]
        triggerMode = integer(default=0, min=0, max=2)
