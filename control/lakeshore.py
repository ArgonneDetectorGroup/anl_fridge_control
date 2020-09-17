import serial

class TempControl:
    def __init__(self, address, channames):
        if len(channames) != 4:
            print('ERROR: Incorrect number of channel names.')
            return
        
        self.connex = serial.Serial(port='/dev/ttyr18', baudrate=9600, parity=serial.PARITY_ODD, stopbits=serial.STOPBITS_ONE, bytesize=serial.SEVENBITS, timeout=1)
        self.channel_names = channames

    def get_temps(self):
        self.connex.write(('KRDG? %s\r\n'%(self.channel_names[0])).encode())
        w=self.connex.readline().decode()
        self.connex.write(('KRDG? %s\r\n'%(self.channel_names[1])).encode())
        x=self.connex.readline().decode()
        self.connex.write(('KRDG? %s\r\n'%(self.channel_names[2])).encode())
        y=self.connex.readline().decode()
        self.connex.write(('KRDG? %s\r\n'%(self.channel_names[3])).encode())
        z=self.connex.readline().decode()
        temps={str(self.channel_names[0]):w.strip('\r\n'), str(self.channel_names[1]):x.strip('\r\n'), str(self.channel_names[2]):y.strip('\r\n'), str(self.channel_names[3]):z.strip('\r\n')}
        return temps
    
#    def read_queue(self):
#        x=self.connex.readline()
#        return x

#    def get_temps(self):
#        output = self.query_temps()
#        for i in range(len(self.channel_names)):
#                temps = {self.channel_names[i]:float(output[i])}
#       for i in range(len(self.channel_names)):
#            temps[self.channel_names[i]]=float(output[i])
#        return temps

    def set_heater_range(self, range):
        if range in [0,1,2,3,4,5]:
            self.connex.write(('RANGE %d\r\n'%(range)).encode())
        else:
            print('ERROR: Heater range outside of allowed range.')

    def set_PID_temp(self, output, temp):
         if output in [1,2]:
             self.connex.write(('SETP %d,%f\r\n'%(output, temp)).encode())
         else:
            print('ERROR: Output outside of allowed range.')

    def set_PID_params(self, output, P, I, D):
        self.connex.write(('PID %d,%f,%f,%f\r\n'%(output,P,I,D)).encode())

    def get_HTR_output(self):
        command='HTR?\r\n'
        try: #py2
            self.connex.write(command)
        except: #py3
            self.connex.write(command.encode('utf-8'))
        return self.connex.readline()
    def config_output(self, output, mode, input):
        if output in [1,2] and mode in range(6) and input in range(5):
            command='OUTMODE %d,%d,%d,0\r\n'%(output, mode, input)
            try: #py2
                self.connex.write(command)
            except: #py3
                self.connex.write(command.encode('utf-8'))
        else:
            print('ERROR: Heater output, mode, or input outside of allowed range!')
