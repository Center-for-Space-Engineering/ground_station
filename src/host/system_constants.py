'''
    This files holds the definition of where to find different tools that the system has access to. 
    The main purpose of this is to help the sensors class have very few imports. 
'''
#CSE system information
interface_listener_list = {}
server = None
sensors_config = {}
database_name = ''
board_serial_listener_name = ''

#Unpacking CCSDS packets 
ccsds_header_len = b''
sync_word = b''
sync_word_len = b''
packet_len_addr1 = b''
packet_len_addr2 = b''
telemetry_packet_num = 0

#Spesific Packet information
vaild_apids = []
telemetry_packet_types = []
system_clock=0
real_time_clock=0

#instruments dict
instruments = {}