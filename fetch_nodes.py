import json
import urllib.request
import sys
import os
import ssl

API_URL = "https://ip.v2too.top/api/nodes"
OUTPUT_FILE = "nodes.txt"
CACHE_FILE = "region_cache.json"

# ============================================================
# Cloudflare 常用 IATA/区域码 -> ISO 3166-1 alpha-2 国家代码
# ============================================================
REGION_TO_COUNTRY = {
    # 日本
    "NRT": "JP", "HND": "JP", "KIX": "JP", "FUK": "JP",
    "OKA": "JP", "NGO": "JP", "CTS": "JP", "KOJ": "JP",
    "SDJ": "JP", "KMQ": "JP", "HIJ": "JP", "MYJ": "JP",
    "AOJ": "JP", "AKJ": "JP", "AXT": "JP", "GAJ": "JP",
    "KIJ": "JP", "KUH": "JP", "MMB": "JP", "UBJ": "JP",
    "OBO": "JP", "SHM": "JP", "TTJ": "JP", "WKJ": "JP",
    "YGJ": "JP",
    # 新加坡
    "SIN": "SG", "QPG": "SG",
    # 香港
    "HKG": "HK",
    # 台湾
    "TPE": "TW", "KHH": "TW", "RMQ": "TW", "TNN": "TW",
    # 韩国
    "ICN": "KR", "GMP": "KR", "PUS": "KR", "CJU": "KR",
    "TAE": "KR", "KWJ": "KR", "RSU": "KR", "USN": "KR",
    "WJU": "KR", "YNY": "KR",
    # 泰国
    "BKK": "TH", "DMK": "TH", "CNX": "TH", "HKT": "TH",
    "KBV": "TH", "USM": "TH", "UTH": "TH", "UBP": "TH",
    # 越南
    "SGN": "VN", "HAN": "VN", "DAD": "VN", "NHA": "VN",
    "CXR": "VN", "PQC": "VN", "VII": "VN", "HPH": "VN",
    # 马来西亚
    "KUL": "MY", "BKI": "MY", "PEN": "MY", "JHB": "MY",
    "KCH": "MY", "LGK": "MY", "MYY": "MY", "TWU": "MY",
    "KBR": "MY", "TGG": "MY",
    # 印尼
    "CGK": "ID", "DPS": "ID", "SUB": "ID", "MES": "ID",
    "UPG": "ID", "BDO": "ID", "SRG": "ID", "YIA": "ID",
    "KNO": "ID", "PLM": "ID", "PKU": "ID", "BPN": "ID",
    "BDJ": "ID", "LOP": "ID", "SOC": "ID",
    # 菲律宾
    "MNL": "PH", "CEB": "PH", "DVO": "PH", "CRK": "PH",
    "ILO": "PH", "PPS": "PH", "ZAM": "PH", "TAG": "PH",
    # 印度
    "BOM": "IN", "DEL": "IN", "MAA": "IN", "BLR": "IN",
    "HYD": "IN", "CCU": "IN", "AMD": "IN", "PNQ": "IN",
    "COK": "IN", "GOI": "IN", "JAI": "IN", "LKO": "IN",
    "ATQ": "IN", "TRV": "IN", "VNS": "IN", "IXC": "IN",
    "GAU": "IN", "IMF": "IN", "PAT": "IN", "RPR": "IN",
    "BBI": "IN", "IDR": "IN", "NAG": "IN", "VTZ": "IN",
    # 阿联酋
    "DXB": "AE", "AUH": "AE", "SHJ": "AE", "DWC": "AE",
    "RKT": "AE",
    # 沙特
    "RUH": "SA", "JED": "SA", "DMM": "SA", "MED": "SA",
    "AHB": "SA", "TUU": "SA", "GIZ": "SA", "TIF": "SA",
    # 卡塔尔
    "DOH": "QA",
    # 阿曼
    "MCT": "OM", "SLL": "OM",
    # 巴林
    "BAH": "BH",
    # 科威特
    "KWI": "KW",
    # 土耳其
    "IST": "TR", "SAW": "TR", "ESB": "TR", "ADB": "TR",
    "AYT": "TR", "ADA": "TR", "TZX": "TR", "DIY": "TR",
    "ERS": "TR", "VAN": "TR", "DLM": "TR", "BJV": "TR",
    "ASR": "TR", "KCM": "TR", "MQM": "TR", "GZT": "TR",
    "MLX": "TR", "SZF": "TR", "TJK": "TR",
    # 德国
    "FRA": "DE", "MUC": "DE", "BER": "DE", "TXL": "DE",
    "DUS": "DE", "HAM": "DE", "STR": "DE", "CGN": "DE",
    "HAJ": "DE", "NUE": "DE", "LEJ": "DE", "BRE": "DE",
    "DTM": "DE", "FMO": "DE", "DRS": "DE",
    # 英国
    "LHR": "GB", "MAN": "GB", "LGW": "GB", "STN": "GB",
    "LTN": "GB", "EDI": "GB", "BHX": "GB", "GLA": "GB",
    "BRS": "GB", "NCL": "GB", "LBA": "GB", "EMA": "GB",
    "ABZ": "GB", "BFS": "GB", "CWL": "GB", "SOU": "GB",
    # 法国
    "CDG": "FR", "ORY": "FR", "MRS": "FR", "LYS": "FR",
    "NCE": "FR", "TLS": "FR", "BOD": "FR", "NTE": "FR",
    "LIL": "FR", "SXB": "FR", "MPL": "FR", "BES": "FR",
    # 荷兰
    "AMS": "NL", "RTM": "NL", "EIN": "NL", "MST": "NL",
    "GRQ": "NL",
    # 西班牙
    "MAD": "ES", "BCN": "ES", "AGP": "ES", "PMI": "ES",
    "ALC": "ES", "VLC": "ES", "SVQ": "ES", "BIO": "ES",
    "IBZ": "ES", "LPA": "ES", "TFS": "ES", "ACE": "ES",
    "FUE": "ES", "MAH": "ES", "SCQ": "ES", "ZAZ": "ES",
    "VGO": "ES", "GRX": "ES", "OVD": "ES", "XRY": "ES",
    # 葡萄牙
    "LIS": "PT", "OPO": "PT", "FAO": "PT", "FNC": "PT",
    "PDL": "PT", "TER": "PT", "HOR": "PT",
    # 意大利
    "FCO": "IT", "MXP": "IT", "BGY": "IT", "VCE": "IT",
    "BLQ": "IT", "NAP": "IT", "TRN": "IT", "CTA": "IT",
    "PMO": "IT", "CAG": "IT", "GOA": "IT", "FLR": "IT",
    "BRI": "IT", "PSA": "IT", "AOI": "IT", "SUF": "IT",
    "AHO": "IT", "OLB": "IT", "CIY": "IT", "VRN": "IT",
    "TSF": "IT", "REG": "IT", "PEG": "IT",
    # 奥地利
    "VIE": "AT", "SZG": "AT", "INN": "AT", "GRZ": "AT",
    "LNZ": "AT", "KLU": "AT",
    # 瑞士
    "ZRH": "CH", "GVA": "CH", "BSL": "CH", "BRN": "CH",
    "LUG": "CH",
    # 瑞典
    "ARN": "SE", "GOT": "SE", "MMX": "SE", "LLA": "SE",
    "UME": "SE", "NYO": "SE", "VXO": "SE", "KRN": "SE",
    "OSD": "SE", "VST": "SE",
    # 丹麦
    "CPH": "DK", "BLL": "DK", "AAL": "DK", "AAR": "DK",
    # 挪威
    "OSL": "NO", "BGO": "NO", "SVG": "NO", "TRD": "NO",
    "TOS": "NO", "KRS": "NO", "AES": "NO", "BOO": "NO",
    "HAU": "NO", "KSU": "NO", "MOL": "NO",
    # 芬兰
    "HEL": "FI", "TMP": "FI", "TKU": "FI", "OUL": "FI",
    "RVN": "FI", "IVL": "FI", "JOE": "FI", "KUO": "FI",
    "KAJ": "FI",
    # 爱尔兰
    "DUB": "IE", "ORK": "IE", "SNN": "IE", "NOC": "IE",
    "KIR": "IE", "CFN": "IE",
    # 比利时
    "BRU": "BE", "CRL": "BE", "ANR": "BE", "OST": "BE",
    "LGG": "BE",
    # 卢森堡
    "LUX": "LU",
    # 波兰
    "WAW": "PL", "KRK": "PL", "GDN": "PL", "KTW": "PL",
    "WRO": "PL", "POZ": "PL", "RZE": "PL", "SZZ": "PL",
    "LCJ": "PL", "BZG": "PL",
    # 捷克
    "PRG": "CZ", "BRQ": "CZ", "OSR": "CZ", "PED": "CZ",
    "KLV": "CZ",
    # 匈牙利
    "BUD": "HU", "DEB": "HU",
    # 罗马尼亚
    "OTP": "RO", "BUH": "RO", "CLJ": "RO", "TSR": "RO",
    "IAS": "RO", "CND": "RO", "SBZ": "RO", "OMR": "RO",
    # 保加利亚
    "SOF": "BG", "VAR": "BG", "BOJ": "BG", "PDV": "BG",
    # 克罗地亚
    "ZAG": "HR", "DBV": "HR", "SPU": "HR", "PUY": "HR",
    "ZAD": "HR", "RJK": "HR", "OSI": "HR",
    # 希腊
    "ATH": "GR", "SKG": "GR", "HER": "GR", "RHO": "GR",
    "CHQ": "GR", "CFU": "GR", "JMK": "GR", "ZTH": "GR",
    "JTR": "GR", "KGS": "GR", "KLX": "GR", "EFL": "GR",
    "PVK": "GR", "AXD": "GR", "IOA": "GR", "VOL": "GR",
    # 俄罗斯
    "SVO": "RU", "DME": "RU", "LED": "RU", "VKO": "RU",
    "AER": "RU", "KZN": "RU", "OVB": "RU", "SVX": "RU",
    "KRR": "RU", "UFA": "RU", "ROV": "RU", "GOJ": "RU",
    "KUF": "RU", "OMS": "RU", "CEK": "RU", "NUX": "RU",
    "KGD": "RU", "MMK": "RU", "PKC": "RU", "VVO": "RU",
    "KHV": "RU", "IKT": "RU", "BQS": "RU", "YKS": "RU",
    # 乌克兰
    "KBP": "UA", "LWO": "UA", "ODS": "UA", "HRK": "UA",
    "IEV": "UA", "DNK": "UA", "UDJ": "UA",
    # 以色列
    "TLV": "IL", "ETH": "IL", "HFA": "IL", "VDA": "IL",
    # 约旦
    "AMM": "JO", "AQJ": "JO",
    # 黎巴嫩
    "BEY": "LB",
    # 塞浦路斯
    "LCA": "CY", "PFO": "CY", "ECN": "CY",
    # 马耳他
    "MLA": "MT",
    # 冰岛
    "KEF": "IS", "RKV": "IS", "AEY": "IS", "EGS": "IS",
    # 拉脱维亚
    "RIX": "LV",
    # 立陶宛
    "VNO": "LT", "KUN": "LT", "PLQ": "LT",
    # 爱沙尼亚
    "TLL": "EE",
    # 斯洛文尼亚
    "LJU": "SI",
    # 斯洛伐克
    "BTS": "SK", "KSC": "SK",
    # 塞尔维亚
    "BEG": "RS", "INI": "RS",
    # 阿尔巴尼亚
    "TIA": "AL",
    # 北马其顿
    "SKP": "MK",
    # 波黑
    "SJJ": "BA",
    # 白俄罗斯
    "MSQ": "BY",
    # 摩尔多瓦
    "KIV": "MD",
    # 亚美尼亚
    "EVN": "AM",
    # 格鲁吉亚
    "TBS": "GE", "KUT": "GE",
    # 阿塞拜疆
    "GYD": "AZ",
    # 哈萨克斯坦
    "ALA": "KZ", "NQZ": "KZ", "TSE": "KZ", "CIT": "KZ",
    "SCO": "KZ", "AKX": "KZ", "URA": "KZ", "GUW": "KZ",
    # 乌兹别克斯坦
    "TAS": "UZ", "SKD": "UZ", "BHK": "UZ", "NMA": "UZ",
    # 吉尔吉斯斯坦
    "FRU": "KG", "OSS": "KG",
    # 塔吉克斯坦
    "DYU": "TJ",
    # 土库曼斯坦
    "ASB": "TM",
    # 蒙古
    "UBN": "MN", "ULN": "MN",
    # 尼泊尔
    "KTM": "NP",
    # 孟加拉
    "DAC": "BD", "CGP": "BD", "ZYL": "BD",
    # 斯里兰卡
    "CMB": "LK", "HRI": "LK",
    # 马尔代夫
    "MLE": "MV",
    # 巴基斯坦
    "ISB": "PK", "KHI": "PK", "LHE": "PK", "PEW": "PK",
    "SKT": "PK", "MUX": "PK", "UET": "PK", "GIL": "PK",
    "LYP": "PK",
    # 缅甸
    "RGN": "MM", "MDL": "MM", "NYU": "MM",
    # 柬埔寨
    "PNH": "KH", "REP": "KH", "KOS": "KH",
    # 老挝
    "VTE": "LA", "LPQ": "LA", "PKZ": "LA",
    # 文莱
    "BWN": "BN",
    # 东帝汶
    "DIL": "TL",
    # 巴布亚新几内亚
    "POM": "PG",
    # 斐济
    "NAN": "FJ", "SUV": "FJ",
    # 新喀里多尼亚
    "NOU": "NC",
    # 法属波利尼西亚
    "PPT": "PF",
    # 关岛
    "GUM": "GU",
    # 北马里亚纳
    "SPN": "MP",
    # 帕劳
    "ROR": "PW",
    # 马绍尔群岛
    "MAJ": "MH",
    # 密克罗尼西亚
    "KSA": "FM", "PNI": "FM", "TKK": "FM", "YAP": "FM",

    # ===== 北美洲 =====
    # 美国
    "JFK": "US", "EWR": "US", "LGA": "US", "ORD": "US",
    "MDW": "US", "LAX": "US", "SFO": "US", "SJC": "US",
    "OAK": "US", "SEA": "US", "DFW": "US", "IAD": "US",
    "DCA": "US", "BWI": "US", "ATL": "US", "MIA": "US",
    "FLL": "US", "PBI": "US", "MCO": "US", "TPA": "US",
    "BOS": "US", "DEN": "US", "PHX": "US", "MSP": "US",
    "DTW": "US", "PHL": "US", "CLT": "US", "IAH": "US",
    "HOU": "US", "SAN": "US", "LAS": "US", "PDX": "US",
    "SLC": "US", "MCI": "US", "STL": "US", "RDU": "US",
    "AUS": "US", "SAT": "US", "BNA": "US", "IND": "US",
    "CMH": "US", "CLE": "US", "PIT": "US", "CVG": "US",
    "MKE": "US", "MSY": "US", "JAX": "US", "MEM": "US",
    "OKC": "US", "OMA": "US", "ABQ": "US", "TUS": "US",
    "SMF": "US", "SNA": "US", "BUR": "US", "ONT": "US",
    "PSP": "US", "BZN": "US", "BOI": "US", "GEG": "US",
    "RNO": "US", "COS": "US", "ELP": "US", "MAF": "US",
    "LBB": "US", "AMA": "US", "ICT": "US", "TUL": "US",
    "XNA": "US", "LIT": "US", "BHM": "US", "HSV": "US",
    "MOB": "US", "PNS": "US", "GNV": "US", "TLH": "US",
    "SAV": "US", "CHS": "US", "CAE": "US", "GSO": "US",
    "AVL": "US", "TYS": "US", "LEX": "US", "SDF": "US",
    "EVV": "US", "FWA": "US", "SBN": "US", "GRR": "US",
    "LAN": "US", "FNT": "US", "TVC": "US", "MQT": "US",
    "DLH": "US", "RST": "US", "FSD": "US", "FAR": "US",
    "BIS": "US", "GFK": "US", "BIL": "US", "MSO": "US",
    "GJT": "US", "HDN": "US", "ASE": "US", "EGE": "US",
    "JAC": "US", "IDA": "US", "PSC": "US", "EUG": "US",
    "MFR": "US", "RDM": "US", "SCK": "US", "FAT": "US",
    "BFL": "US", "SBA": "US", "SBP": "US", "MRY": "US",
    "STS": "US", "ACV": "US", "OTH": "US", "PDT": "US",
    "ALW": "US", "LWS": "US", "PIH": "US", "TWF": "US",
    "HLN": "US", "BTM": "US", "CPR": "US", "CYS": "US",
    "LAR": "US", "RKS": "US", "COD": "US", "WYS": "US",
    "HNL": "US", "OGG": "US", "KOA": "US", "LIH": "US",
    "ITO": "US", "ANC": "US", "FAI": "US", "JNU": "US",
    "KTN": "US", "SIT": "US", "ADQ": "US", "BET": "US",
    "OTZ": "US", "OME": "US", "BRW": "US", "SCC": "US",
    # 加拿大
    "YYZ": "CA", "YVR": "CA", "YUL": "CA", "YYC": "CA",
    "YEG": "CA", "YOW": "CA", "YWG": "CA", "YHZ": "CA",
    "YQB": "CA", "YQR": "CA", "YXE": "CA", "YYJ": "CA",
    "YTZ": "CA", "YHM": "CA", "YKF": "CA", "YXU": "CA",
    "YQG": "CA", "YQT": "CA", "YSB": "CA", "YYB": "CA",
    "YAM": "CA", "YFC": "CA", "YSJ": "CA", "YYG": "CA",
    "YDF": "CA", "YYT": "CA", "YFB": "CA", "YXY": "CA",
    "YZF": "CA", "YCD": "CA", "YLW": "CA", "YXS": "CA",
    "YMM": "CA", "YQU": "CA", "YYY": "CA", "YBX": "CA",
    # 墨西哥
    "MEX": "MX", "CUN": "MX", "GDL": "MX", "MTY": "MX",
    "TIJ": "MX", "SJD": "MX", "PVR": "MX", "BJX": "MX",
    "QRO": "MX", "MID": "MX", "HMO": "MX", "CUU": "MX",
    "VER": "MX", "ACA": "MX", "ZIH": "MX", "OAX": "MX",
    "TLC": "MX", "CUL": "MX", "LAP": "MX", "MZT": "MX",
    "REX": "MX", "NLD": "MX", "SLP": "MX", "TGZ": "MX",
    "CME": "MX", "PBC": "MX", "VSA": "MX",

    # ===== 南美洲 =====
    "GRU": "BR", "GIG": "BR", "BSB": "BR", "CNF": "BR",
    "CGH": "BR", "VCP": "BR", "POA": "BR", "SSA": "BR",
    "REC": "BR", "FOR": "BR", "BEL": "BR", "CWB": "BR",
    "FLN": "BR", "NAT": "BR", "VIX": "BR", "MAO": "BR",
    "CGB": "BR", "UDI": "BR", "SDU": "BR", "GYN": "BR",
    "EZE": "AR", "AEP": "AR", "COR": "AR", "MDZ": "AR",
    "ROS": "AR", "TUC": "AR", "BRC": "AR", "USH": "AR",
    "SCL": "CL", "ANF": "CL", "PMC": "CL", "CCP": "CL",
    "ZCO": "CL", "PUQ": "CL", "IQQ": "CL", "CJC": "CL",
    "BOG": "CO", "MDE": "CO", "CLO": "CO", "BAQ": "CO",
    "CTG": "CO", "BGA": "CO", "PEI": "CO", "CUC": "CO",
    "LIM": "PE", "CUZ": "PE", "AQP": "PE", "TRU": "PE",
    "PIU": "PE", "IQT": "PE", "PEM": "PE", "JUL": "PE",
    "UIO": "EC", "GYE": "EC", "LTX": "EC", "MEC": "EC",
    "CUE": "EC", "OCC": "EC",
    "CCS": "VE", "MAR": "VE", "VLN": "VE", "BRM": "VE",
    "LPB": "BO", "VVI": "BO", "CBB": "BO",
    "ASU": "PY", "AGT": "PY",
    "MVD": "UY", "PDP": "UY",
    "BJM": "SR",  # Paramaribo (actually PBM)
    "PBM": "SR",
    "GEO": "GY", "OGL": "GY",

    # ===== 中美洲 =====
    "PTY": "PA", "DAV": "PA",
    "SJO": "CR", "LIR": "CR",
    "MGA": "NI",
    "SAL": "SV",
    "SAP": "HN", "TGU": "HN",
    "GUA": "GT", "FRS": "GT",
    "BZE": "BZ",
    "LPX": "BZ",

    # ===== 加勒比 =====
    "HAV": "CU", "VRA": "CU", "HOG": "CU", "SCU": "CU",
    "KIN": "JM", "MBJ": "JM",
    "NAS": "BS", "FPO": "BS", "GGT": "BS",
    "SDQ": "DO", "PUJ": "DO", "POP": "DO", "STI": "DO",
    "PAP": "HT", "CAP": "HT",
    "SJU": "PR", "BQN": "PR", "PSE": "PR",
    "ANU": "AG",
    "BGI": "BB",
    "POS": "TT", "TAB": "TT",
    "GND": "GD",
    "UVF": "LC",
    "SVD": "VC",
    "CUR": "CW",
    "AUA": "AW",
    "SXM": "SX",
    "BON": "BQ",
    "PLS": "TC",
    "GCM": "KY",
    "BDA": "BM",
    "STT": "VI", "STX": "VI",

    # ===== 非洲 =====
    "JNB": "ZA", "CPT": "ZA", "DUR": "ZA", "PLZ": "ZA",
    "ELS": "ZA", "GRJ": "ZA", "BFN": "ZA",
    "LOS": "NG", "ABV": "NG", "PHC": "NG", "KAN": "NG",
    "ENU": "NG", "QOW": "NG", "BNI": "NG",
    "NBO": "KE", "MBA": "KE", "KIS": "KE", "EDL": "KE",
    "ADD": "ET", "DIR": "ET",
    "DAR": "TZ", "ZNZ": "TZ", "JRO": "TZ",
    "EBB": "UG", "KGL": "RW",
    "CMN": "MA", "RAK": "MA", "AGA": "MA", "TNG": "MA",
    "FEZ": "MA", "OUD": "MA", "AHU": "MA", "NDR": "MA",
    "ERH": "MA",
    "CAI": "EG", "HRG": "EG", "SSH": "EG", "LXR": "EG",
    "HBE": "EG", "ASW": "EG", "ATZ": "EG",
    "TUN": "TN", "DJE": "TN", "MIR": "TN", "SFA": "TN",
    "ALG": "DZ", "ORN": "DZ", "CZL": "DZ", "AAE": "DZ",
    "TMR": "DZ",
    "TIP": "LY", "BEN": "LY",
    "KRT": "SD", "PZU": "SD",
    "ACC": "GH", "KMS": "GH", "TKD": "GH",
    "DKR": "SN",
    "ABJ": "CI",
    "OUA": "BF",
    "BKO": "ML",
    "NIM": "NE",
    "COO": "BJ",
    "LFW": "TG",
    "DLA": "CM", "YAO": "CM",
    "LBV": "GA",
    "FIH": "CD", "LAD": "AO",
    "TNR": "MG",
    "MPM": "MZ",
    "LLW": "MW",
    "LUN": "ZM",
    "HRE": "ZW",
    "WDH": "NA",
    "GBE": "BW",
    "SEZ": "SC",
    "MRU": "MU",
    "CUR": "CW",  # already above but fine

    # ===== 大洋洲 =====
    "SYD": "AU", "MEL": "AU", "BNE": "AU", "PER": "AU",
    "ADL": "AU", "CBR": "AU", "DRW": "AU", "HBA": "AU",
    "CNS": "AU", "OOL": "AU", "TSV": "AU", "MCY": "AU",
    "NTL": "AU", "LST": "AU", "AVV": "AU",
    "AKL": "NZ", "CHC": "NZ", "WLG": "NZ", "ZQN": "NZ",
    "DUD": "NZ", "HLZ": "NZ", "PMR": "NZ", "NSN": "NZ",
    "NPE": "NZ", "GIS": "NZ", "NPL": "NZ", "TRG": "NZ",
    "ROT": "NZ", "BHE": "NZ", "IVC": "NZ",
    # ===== 中国 =====
    "PEK": "CN", "PKX": "CN", "PVG": "CN", "SHA": "CN",
    "CAN": "CN", "SZX": "CN", "CTU": "CN", "CKG": "CN",
    "NKG": "CN", "WUH": "CN", "XIY": "CN", "XMN": "CN",
    "HGH": "CN", "CGO": "CN", "TNA": "CN", "KMG": "CN",
    "KWE": "CN", "LHW": "CN", "URC": "CN", "HRB": "CN",
    "SHE": "CN", "DLC": "CN", "TSN": "CN", "TAO": "CN",
    "CSX": "CN", "NNG": "CN", "HAK": "CN", "SYX": "CN",
    "FOC": "CN", "HET": "CN", "TYN": "CN", "SJW": "CN",
    "INC": "CN", "XNN": "CN", "LJG": "CN", "DYG": "CN",
    "WNZ": "CN", "NGB": "CN", "JJN": "CN", "CZX": "CN",
    "WUX": "CN", "NTG": "CN", "YNT": "CN", "WEH": "CN",
    "LYG": "CN", "YNJ": "CN", "MDG": "CN", "JMU": "CN",
    "YBP": "CN", "LZO": "CN", "YIH": "CN", "ENH": "CN",
    "WXN": "CN", "JIQ": "CN", "ZUH": "CN", "SWA": "CN",
    "HUZ": "CN", "BHY": "CN", "YTY": "CN", "HSN": "CN",
    "JHG": "CN", "LUM": "CN", "TCZ": "CN", "BSD": "CN",
    "DIG": "CN", "LNJ": "CN", "BSD": "CN",
    "MFM": "MO",
    "MFM": "CN",  # Macau often uses CN
    # ===== 伊朗 =====
    "IKA": "IR", "THR": "IR", "MHD": "IR", "SYZ": "IR",
    "TBZ": "IR", "IFN": "IR", "AWZ": "IR", "KER": "IR",
    "BND": "IR", "GSM": "IR",
    # ===== 伊拉克 =====
    "BGW": "IQ", "BSR": "IQ", "EBL": "IQ", "NJF": "IQ",
    "ISU": "IQ",
    # ===== 叙利亚 =====
    "DAM": "SY", "ALP": "SY", "LTK": "SY",
    # ===== 也门 =====
    "SAH": "YE", "ADE": "YE", "TAI": "YE",
    # ===== 埃塞俄比亚 =====
    "ADD": "ET", "DIR": "ET", "AMH": "ET", "GDE": "ET",
    # ===== 刚果等 =====
    "FBM": "CD", "GOM": "CD",
    "BZV": "CG",
    "LFW": "TG",
    "SSG": "GQ",
    # ===== 利比亚等 =====
    "MJI": "LY",
    "LAD": "AO",
    "FIH": "CD",
    # 其他补充
    "DSS": "SN", "CSK": "SN",
    "BJL": "GM",
    "FNA": "SL",
    "ROB": "LR",
    "ABJ": "CI",
    "OUA": "BF",
    "BKO": "ML",
    "NIM": "NE",
    "NDJ": "TD",
    "COO": "BJ",
    "LFW": "TG",
    "DLA": "CM",
    "YAO": "CM",
    "NSI": "CM",
    "LBV": "GA",
    "FIH": "CD",
    "FBM": "CD",
    "GOM": "CD",
    "BZV": "CG",
    "SSG": "GQ",
    "LAD": "AO",
    "TNR": "MG",
    "MPM": "MZ",
    "LUN": "ZM",
    "HRE": "ZW",
    "WDH": "NA",
    "GBE": "BW",
    "MSU": "LS",
    "SHO": "SZ",
    "MTS": "SZ",
}


def load_cache():
    """加载本地缓存，避免重复 API 查询"""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_cache(cache):
    """保存缓存到本地文件"""
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def lookup_region_online(region_code):
    """
    通过免费 API 查询 IATA 代码对应的国家。
    使用 travelpayouts.com 的公开机场数据库 (免费, 无需认证)
    """
    airports_url = "https://api.travelpayouts.com/data/en/airports.json"
    try:
        ctx = ssl.create_default_context()
        req = urllib.request.Request(airports_url, headers={"User-Agent": "GitHub-Action"})
        with urllib.request.urlopen(req, timeout=60, context=ctx) as resp:
            airports = json.loads(resp.read().decode("utf-8"))

        # 构建 IATA -> country_code 映射
        iata_map = {}
        for ap in airports:
            code = ap.get("code", "").strip().upper()
            country = ap.get("country_code", "").strip().upper()
            if code and country:
                iata_map[code] = country

        print(f"  Loaded {len(iata_map)} airport codes from online database")
        return iata_map
    except Exception as e:
        print(f"  Warning: Failed to fetch airport database: {e}")
        return {}


def get_country(region_code, cache):
    """获取 region 对应的国家代码，优先缓存 -> 本地映射 -> 在线查询"""
    region_code = region_code.strip().upper()
    if not region_code:
        return None

    # 1. 检查本地缓存
    if region_code in cache:
        return cache[region_code]

    # 2. 检查内置映射
    if region_code in REGION_TO_COUNTRY:
        country = REGION_TO_COUNTRY[region_code]
        cache[region_code] = country
        return country

    # 3. 在线查询
    print(f"  Region '{region_code}' not in local map, querying online database...")
    iata_map = lookup_region_online(region_code)
    if iata_map:
        # 合并到缓存
        for code, country in iata_map.items():
            if code not in cache:
                cache[code] = country

        if region_code in iata_map:
            return iata_map[region_code]

    # 4. 兜底：返回原始代码
    print(f"  Warning: Could not resolve region '{region_code}', using as-is")
    cache[region_code] = region_code
    return region_code


def main():
    # 加载缓存
    cache = load_cache()

    # 请求 API
    try:
        ctx = ssl.create_default_context()
        req = urllib.request.Request(API_URL, headers={"User-Agent": "GitHub-Action"})
        with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"Error fetching API: {e}", file=sys.stderr)
        sys.exit(1)

    # 兼容两种响应格式
    if isinstance(data, list):
        nodes = data
    elif isinstance(data, dict):
        nodes = data.get("value", [])
    else:
        print(f"Unexpected API response type: {type(data)}", file=sys.stderr)
        sys.exit(1)

    if not nodes:
        print("No nodes found in API response", file=sys.stderr)
        sys.exit(1)

    # 过滤 speed >= 50，转换 region -> 国家代码
    lines = []
    filtered_count = 0
    unresolved_regions = set()

    for node in nodes:
        ip = node.get("ip", "")
        region = node.get("region", "")
        speed = node.get("speed", 0)

        # 过滤 speed < 50
        if speed < 50:
            filtered_count += 1
            continue

        if ip and region:
            country = get_country(region, cache)
            if country == region:
                unresolved_regions.add(region)
            lines.append(f"{ip}#{country}")

    # 保存缓存
    save_cache(cache)

    if not lines:
        print("No nodes matched criteria (speed >= 50)", file=sys.stderr)
        sys.exit(1)

    output = "\n".join(lines) + "\n"

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(output)

    print(f"Total nodes: {len(nodes)}, filtered (speed<50): {filtered_count}, output: {len(lines)}")
    if unresolved_regions:
        print(f"Unresolved regions (used as-is): {', '.join(sorted(unresolved_regions))}")
    print("---")
    print(output.strip())


if __name__ == "__main__":
    main()
