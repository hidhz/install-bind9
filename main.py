import os
from time import sleep
from data import *

IP1 = IP.split(".")

os.system("clear")
print("""
 _     _           _  ___    _           _        _ _           _
| |__ (_)_ __   __| |/ _ \  (_)_ __  ___| |_ __ _| | | __ _ ___(_)
| '_ \| | '_ \ / _` | (_) | | | '_ \/ __| __/ _` | | |/ _` / __| |
| |_) | | | | | (_| |\__, | | | | | \__ \ || (_| | | | (_| \__ \ |
|_.__/|_|_| |_|\__,_|  /_/  |_|_| |_|___/\__\__,_|_|_|\__,_|___/_|
""")
print("\x1b[6;30;42m"+"By : hidha //-dev \n\n"+"\x1b[0m")
# Konfigurasi hosts
print("00. konfigurasi hosts...")
sleep(1)
os.chdir("/etc")
hosts = f"""
# IPv4.
127.0.0.1   localhost
127.0.1.1   srv1
{IP}   {DOMAIN}

# IPv6.
::1         ip6-localhost ip6-loopback
fe00::0     ip6-localnet
ff00::0     ip6-mcastprefix
ff02::1     ip6-allnodes                                                  
ff02::2     ip6-allrouters
"""
with open("hosts", "w") as f :
  f.write(hosts)
  
# Konfigurasi ip address
print("01. konfigurasi ip address...")
sleep(1)
os.chdir("network")
with open("interfaces", "a") as f :
  f.write(f"""auto {INET}
iface {INET} inet static
	address {IP}
	gateway {GATEWAY}
	""")
# restart network
print("restarting network...")
os.system("nmcli off")
os.system("nmcli on")
os.system("systemctl restart NetworkManager")
sleep(.5)
print("konfigurasi ip address selesai...")
sleep(1)
os.system("clear")

# Install bind9
print("02. Memulai Install bind9...")
sleep(1)
os.system("apt update -y")
os.system("apt install bind9 bind9utils bind9-doc dnsutils bind9-dnsutils bind9-host -y")
sleep(.5)
print("install bind9 selesai...")
sleep(1)
os.system("clear")

# Allow firewall bind9 dan nganu named
os.system("ufw allow Bind9")
os.system("systemctl start named")
os.system("systemctl enable named")

# Konfigurasi file named.conf.local
print("03. Mengedit file named.conf.local")
sleep(1)
os.chdir("../bind")
text = [ "",
	  f'zone "{DOMAIN}"','{',
	  '	type master;',
	  '	file "/etc/bind/db.domain";',
	  '};',
	  '',
	  f'zone "{IP1[2]}.{IP1[1]}.{IP1[0]}.in-addr.arpa"','{',
	  '	type master;',
	  '	file "/etc/bind/db.ip";',
	  '};'
	]
with open("named.conf.local", "a") as namedConfLocal:
	namedConfLocal.write("\n".join(text))

print("konfigurasi named.conf.local selesai...")
sleep(1)
os.system("clear")

# Konfigurasi file db.domain
print("04. Membuat dan Mengedit file db.domain")
sleep(1)
domainEdit = [
';',
'; BIND data file for local loopback interface',
'$TTL    604800',
f'@       IN      SOA     ns.{DOMAIN}. admin.{DOMAIN}. (',
'                              200       ; Serial',
'                         604800         ; Refresh',
'                          86400         ; Retry',
'                        2419200         ; Expire',
'                         604800 )       ; Negative Cache TTL',
';',
f'{DOMAIN}.      IN     NS     ns.{DOMAIN}.',
f'ns       IN      A     {IP}',
f'www      IN      A	{IP}'
]
with open("db.domain", "w") as dbDomain:
	dbDomain.write("\n".join(domainEdit))
print("konfigurasi db.domain selesai...")
sleep(1)
os.system("clear")

# Konfigurasi file db.ip
print("05. Membuat dan Mengedit file db.ip")
sleep(1)
ipEdit = [
';',
'; BIND reverse data file for local loopback interface',
';',
'$TTL	604800',
f'@	IN	SOA	{DOMAIN}. admin.{DOMAIN}. (',
'			      100	; Serial',
'			 604800		; Refresh',
'			  86400		; Retry',
'			2419200		; Expire',
'			 604800 )	; Negative Cache TTL',
';',
f'IN	NS	ns.{DOMAIN}.',
f'ns	IN	A {IP}',
f'{IP1[3]}	IN	PTR	ns.{DOMAIN}.'
]
with open("db.ip", "w") as dbIp:
	dbIp.write("\n".join(ipEdit))
print("konfigurasi db.ip selesai...")
sleep(1)
os.system("clear")

# konfigurasi file named.conf.options
print("06. Mengedit file named.conf.options")
confOptions = """options {
        directory "/var/cache/bind";

        // If there is a firewall between you and nameservers you want
        // to talk to, you may need to fix the firewall to allow multiple
        // ports to talk.  See http://www.kb.cert.org/vuls/id/800113

        // If your ISP provided one or more IP addresses for stable
        // nameservers, you probably want to use them as forwarders.
        // Uncomment the following block, and insert the addresses replacing
        // the all-0's placeholder.

        forwarders {
              0.0.0.0;
              8.8.8.8;
              8.8.4.4;
        };

        //========================================================================
        // If BIND logs error messages about the root key being expired,
        // you will need to update your keys.  See https://www.isc.org/bind-keys
        //========================================================================
        dnssec-validation auto;

        listen-on-v6 { any; };
};
"""
sleep(1)


# konfigurasi file resolv.conf
print("07. Mengedit file resolv.conf")
sleep(1)
resolv = f"""
search {DOMAIN}
nameserver {IP}
"""
os.chdir("..")
with open("resolv.conf", "a") as rc :
  rc.write(resolv)
print("Edit file selesai...")
os.system("clear")

# Restart
print("restart named dan bind9 service...")
sleep(1)
os.system("systemctl restart named")
sleep(.5)
os.system("systemctl restart bind9")
os.system("systemctl restart bind9.service")
os.system("service bind9 restart")
sleep(.5)

# Selesai
os.system("clear")
print("---KONFIGURAS DNS SERVER SELESAI---")
print("""----------***************-----------
Untuk pengujian, banyak caranya bisa ketik salah satu ini diterminal
1. dig hidhz.dev (nama domain)
2. nslookup hidhz.dev 192.168.70.1
3. ping hidhz.dev (nama domain)
""")
print("----------***************-----------")
print("\x1b[6;30;42m"+"By : hidha //-dev \n\n"+"\x1b[0m")