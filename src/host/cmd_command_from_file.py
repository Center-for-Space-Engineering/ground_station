'''
    This class shows and example of how to implement a command on the server. 
'''
from commandParent import commandParent # pylint: disable=e0401
from command_packets.functions import ccsds_crc16

#import DTO for communicating internally
from logging_system_display_python_api.DTOs.print_message_dto import print_message_dto # pylint: disable=e0401

class cmd_command_from_file(commandParent):
    '''
        The init function goes to the cmd class and then populates its 
        self into its command dict so that it is dynamically added to the command repo
    '''
    def __init__(self, CMD, coms):
        # init the parent
        super().__init__(CMD, coms=coms, called_by_child=True)
        #CMD is the cmd class and we are using it to hold all the command class
        self.__commandName = 'example'
        self.__args ={
            "create_packet" : self.create_packet,
            "send_packet" : self.send_packet
        }
        dictCmd = CMD.get_command_dict()
        dictCmd[self.__commandName] = self #this is the name the web server will see, so to call the command send a request for this command. 
        CMD.setCommandDict(dictCmd)
        self.__coms = coms
        self.__packet_count = 0

    def run(self):
        '''
            Runs a call from the server, with no args!
        '''
        print("Ran command")
        dto  = print_message_dto("Ran command")
        self.__coms.print_message(dto, 2)
        return f"<p>ran command {self.__commandName}<p>"
    def run_args(self, args):
        '''
            This function is what allows the server to call function in this class
            ARGS:
                [0] : function name
                [1:] ARGS that the function needs. NOTE: can be blank
        '''
        print(f"ran command {str(args[0])} with args {str(args[1:])}")
        try:
            message = self.__args[args[0]](args)
            dto = print_message_dto(message)
            self.__coms.print_message(dto, 2)
        except Exception as e: # pylint: disable=w0718
            message += f"<p> Not valid arg Error {e}</p>"
        return message
    def create_packet(self, args):
        '''
            creates a byte array for a packet given a byte array with the packet contents and an APID.
        '''
        bytes_filename = args[1]
        packet_apid = args[2]

        #Import bytearray from file
        try:
            with open(bytes_filename, 'rb') as file:
                data = file.read()
            byte_data = bytearray(data)
        except FileNotFoundError:
            return f"Error: File '{bytes_filename}' not found."
        except IOError:
            return f"Error: Unable to read file '{bytes_filename}'."

        packet_version_number = 0
        packet_type = 1
        secondary_header = 0
        sequence_flags = 0
        packet_count = self.__packet_count
        packet_length = len(byte_data)
        # self.__packet_count += 1

        header_byte1 = ((packet_version_number & 0b111) << 5) | ((packet_type & 0b1) << 4) | ((secondary_header & 0b1) << 3) | ((packet_apid & 0b11100000000) >> 8)
        header_byte2 = (packet_apid & 0b00011111111)
        header_byte3 = ((sequence_flags & 0b11) << 6) | ((packet_count & 0b11111100000000) >> 8)
        header_byte4 = (packet_count & 0b00000011111111)
        header_byte5 = (packet_length & 0xFF00)
        header_byte6 = (packet_length & 0x00FF)

        header = bytearray([header_byte1, header_byte2, header_byte3, header_byte4, header_byte5, header_byte6])

        bytes_for_crc = header + byte_data

        crc = ccsds_crc16(data=bytes_for_crc)
        
        crc_bytes = crc.to_bytes(2, byteorder='big')

        packet_bytes = bytes_for_crc + crc_bytes

        self.__packet_bytes = packet_bytes

        formatted_bytes = [f'\\x{byte:02x}' for byte in packet_bytes]
        formatted_bytes =  ''.join(formatted_bytes)


        print("ran create_packets")
        dto = print_message_dto("Ran create_packets")
        self.__coms.print_message(dto, 2)
        return f"<p>ran command create_packets with args {str(args)}</p><p>{formatted_bytes}<\p>"
    def send_packet(self, _):
        '''
            Sends the created packet to the pi.
        '''
        self.__packet_count += 1

    def get_args(self):
        '''
            This function returns an html obj that explains the args for all the internal
            function calls. 
        '''
        message = ""
        for key in self.__args:
            message += f"<url>/{self.__commandName}/{key}</url><p></p>" #NOTE: by adding the url tag, the client knows this is a something it can call, the <p></p> is basically a new line for html
        return message

    def __str__(self):
        return self.__commandName
    def get_args_server(self):
        '''
            This function returns an html obj that explains the args for all the internal
            function calls. 
        '''
        message = []
        for key in self.__args:
            message.append({ 
            'Name' : key,
            'Path' : f'/{self.__commandName}/{key}/-parameters for the function-',
            'Description' : 'Example commands'    
            })
        return message
