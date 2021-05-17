import random
import socket
import binascii

randID = random.randint(0, 10000)

client = input("my-dns-client: ")
section = client.split(".")

print("Preparing DNS query..")
# 16 bit id uniquely identify query message.
# Note that when you send multiple query messages, you will use this ID to match the responses to queries.
# The ID can be randomly generated by your client program.
header_ID = hex(randID)[2:].zfill(4)

# 0 for query and 1 for response.
# We are only interested in standard query.
# This bit is set if client wants the name server to recursively pursue the query. We will set this to 1.
# qr: 0; opcode: 0000; AA: 0; TC: 0; RD: 1; RA: 0; Z: 000; RCODE: 0000
# 0000 0001 0000 0000 = 0x0100
header_Parameters = "0x0100"[2:]

# Since we are only sending one hostname query at a time, we will set this to 1.
header_QDCount = "0x0001"[2:]
header_ANCount = "0x0000"[2:]
header_NSCount = "0x0000"[2:]
header_ARCount = "0x0000"[2:]

# It contains multiple labels - one for each section of a URL.
# For example, for gmu.edu, there should be two labels for gmu and edu.
# Each label consists of a length octet (3 for gmu), followed by ASCII code octets (67 for g, 6D for m, 75 for u).
# This is repeated for each label of the URL.
# The QNAME terminates with the zero length octet for the null label of the root.
# Note that this field may be an odd number of octets; no padding is used.
q_Name = []
for s in section:
    label = [hex(len(s))[2:].zfill(2)]
    for letter in s:
        label.append(hex(ord(letter))[2:])
    q_Name.append(label)
q_Name.append([hex(0)[2:].zfill(2)])
# Set to 1 because we are only interested in A type records.
# You can ignore NS, MX and CNAME type records for this assignment.
q_Type = hex(1)[2:].zfill(4)
q_Class = hex(1)[2:].zfill(4)

msg = str(header_ID) + str(header_Parameters) + str(header_QDCount) + str(header_ANCount) + str(header_NSCount) + str(
    header_ARCount)

for q_Label in q_Name:
    for q in q_Label:
        msg = msg + q

msg = msg + str(q_Type) + str(q_Class)

#################################################################
print("Contacting DNS server..\nSending DNS query..")
address = ("8.8.8.8", 53)
objConnect = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
for i in range(1, 4):
    try:
        print("DNS response received (attempt ", i, " out of 3)")
        objConnect.settimeout(5)
        objConnect.sendto(binascii.a2b_hex(msg), address)
        receive = objConnect.recv(4096)
    except socket.timeout:
        if i == 3:
            print("Timeout Error\nExiting program..")
            exit(1)
    else:
        objConnect.close()
        break

#################################################################
r_Header_Id = None
r_Header_Parameter = None
r_Header_QDCount = None
r_Header_ANCount = None
r_Header_NSCount = None
r_Header_ARCount = None
r_QName = []
r_QType = None
r_QClass = None
r_AName = None
r_AType = None
r_AClass = None
r_ATTL = None
r_RDLength = None
r_ARDATA = []

print("Processing DNS repsonse..")
interpret = binascii.b2a_hex(receive).decode("utf-8")

partition = []
for i in range(0, len(interpret), 2):
    partition.append(interpret[i:i + 2])

partition_header = []
for i in range(0, 12, 2):
    partition_header.append(" ".join(partition[i:i + 2]))

# Header ID is the first 4 hex
r_Header_Id = "0x" + partition_header[:1][0].replace(" ", "")
print("header.ID =", r_Header_Id)

# Parameters from hex to 16 bit
r_Header_Parameter = bin(int(partition_header[1:2][0].replace(" ", ""), 16))[2:]
r_Header_QR = r_Header_Parameter[:1]
r_Header_OPCODE = r_Header_Parameter[1:5]
r_Header_AA = r_Header_Parameter[5:6]
r_Header_TC = r_Header_Parameter[6:7]
r_Header_RD = r_Header_Parameter[7:8]
r_Header_RA = r_Header_Parameter[8:9]
r_Header_Z = r_Header_Parameter[9:12]
r_Header_RCODE = r_Header_Parameter[12:]
print("header.QR =", r_Header_QR, "\nheader.OPCODE =", r_Header_OPCODE, "\nheader.AA =", r_Header_AA, "\nheader.TC =",
      r_Header_TC, "\nheader.RD =", r_Header_RD, "\nheader.RA =", r_Header_RA, "\nheader.Z =", r_Header_Z,
      "\nheader.RCODE", int(r_Header_RCODE, 2))

# Rest of the headers.
r_Header_QDCount = partition_header[2:3][0].replace(" ", "")
r_Header_ANCount = partition_header[3:4][0].replace(" ", "")
r_Header_NSCount = partition_header[4:5][0].replace(" ", "")
r_Header_ARCount = partition_header[5:][0].replace(" ", "")
print("header.QDCOUNT =", int(r_Header_QDCount, 16), "\nheader.ANCOUNT =", int(r_Header_ANCount, 16),
      "\nheader.NSCOUNT =", int(r_Header_NSCount, 16), "\nheader.ARCOUNT =", int(r_Header_ARCount, 16))

# QName which has the structure of indicating how long a string is then the string.
# Continuous until a length indicator of 0.

position = 12
while 1:
    currValue = partition[position:position + 1]
    currValue = int(currValue[0], 16)
    if currValue > 0:
        r_QName.append(partition[position:position + 1])
        for i in range(currValue):
            position = position + 1
            r_QName.append([partition[position:position + 1][0], chr(int(partition[position:position + 1][0], 16))])
        position = position + 1
    else:
        r_QName.append(partition[position:position + 1])
        break

qName_msg = ""
msgQ = ""
label_count = 0
name_length = 0
for i in r_QName:
    if len(i) == 1:
        label_count = label_count + 1
        name_length = name_length + int(i[0], 16)
        msgQ = msgQ + "."
    else:
        msgQ = msgQ + chr(int(i[0], 16))
label_count = label_count - 1
name_length = name_length + label_count - 1
if name_length < 0:
    name_length = 0
msgQ = msgQ[1:len(msgQ)-1]
qName_msg = "\tName: " + msgQ + "\n\tName length: " + str(name_length) + "\n\tLabel count: " + str(label_count)
print("question.QNAME = \n" + qName_msg)

position = position + 3
r_QType = int(partition[position - 2:position - 1][0] + "" + partition[position - 1:position][0], 16)
qType_Ans = None
if r_QType == 1:
    qType_Ans = "A"
elif r_QType == 0:
    qType_Ans = "AA"
else:
    qType_Ans = "Unknown QTYPE"
print("question.QTYPE =", qType_Ans)

if client != "":
    position = position + 2
    r_QClass = int(partition[position - 2:position - 1][0] + "" + partition[position - 1:position][0], 16)
    qClass_Ans = None
    if r_QClass == 1:
        qClass_Ans = "IN"
    elif r_QClass == 0:
        qClass_Ans = "Reserved"
    else:
        qClass_Ans = "Unknown Class"
    print("question.QCLASS =", qClass_Ans)

    position = position + 2
    r_AName = "0x" + partition[position - 2:position - 1][0] + "" + partition[position - 1:position][0]
    print("answer.NAME =", r_AName)

    position = position + 2
    r_AType = int(partition[position - 2:position - 1][0] + "" + partition[position - 1:position][0], 16)
    r_atype_ans = None
    if r_AType == 1:
        r_atype_ans = "A"
    elif r_AType == 0:
        r_atype_ans = "AA"
    else:
        r_atype_ans = "Unknown ATYPE"

    print("answer.TYPE =", r_atype_ans)

    position = position + 2
    r_AClass = int(partition[position - 2:position - 1][0] + "" + partition[position - 1:position][0], 16)
    r_aclass_ans = None
    if r_AClass == 1:
        r_aclass_ans = "IN"
    elif r_AClass == 0:
        r_aclass_ans = "Reserved"
    else:
        r_aclass_ans = "Unknown Class"

    print("answer.CLASS =", r_aclass_ans)

    position = position + 4
    r_ATTL = partition[position - 4:position - 3][0] + partition[position - 3:position - 2][0] + \
             partition[position - 2:position - 1][0] + partition[position - 1:position][0]
    print("answer.TTL =", int(r_ATTL, 16), "seconds")

    position = position + 2
    r_RDLength = int(partition[position - 2:position - 1][0] + "" + partition[position - 1:position][0], 16)
    print("answer.RDLENGTH =", r_RDLength)

    r_ARDATA = partition[position:]
    RDATA_IP = []
    ip_list = "\n"
    for i in range(0, len(r_ARDATA), 4):
        RDATA_IP.append(r_ARDATA[i:i + 4])
    for ip in RDATA_IP:
        ip_address = ""
        for x in ip:
            ip_address = ip_address + str(int(x, 16)) + "."
        ip_address = ip_address[:len(ip_address) - 1]
        ip_list = ip_list + "\t" + ip_address + "\n"
    print("answer.RDATA =", ip_list)
else:
    print("<NO ANSWER>")
input("Press Enter To Close")
exit(0)
