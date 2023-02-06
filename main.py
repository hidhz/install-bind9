import os
from time import sleep
from data import *

IP1 = IP.split(".")

os.system("clear")

# Konfigurasi hosts
print("00. konfigurasi hosts...")
sleep(1)
os.system("nano /etc/hosts")
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
# Konfigurasi ip address
print("01. konfigurasi ip address...")
sleep(1)
os.chdir("/etc/network")
with open("interfaces", "a") as f :
        f.write(f"""auto {ETH}
iface {ETH} inet static
	address {IP}
	gateway {GATEWAY}""")
# restart network
print("restarting network...")
os.system("systemctl restart networking")
sleep(.5)
print("konfigurasi ip address selesai...")
sleep(1)
os.system("clear")

# Allow firewall bind9
os.system("ufw allow Bind9")

# Install bind9
print("02. Memulai Install bind9...")
sleep(1)
os.system("apt update -y")
os.system("apt install bind9 bind9utils bind9-doc dnsutils -y")
sleep(.5)
print("install bind9 selesai...")
sleep(1)
os.system("clear")

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
f'@       IN      SOA     {DOMAIN}. admin.{DOMAIN}. (',
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
f'1	IN	PTR	{DOMAIN}.',
f'ns	IN	A	{IP}'
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
nameserver {DOMAIN}
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
os.system("systemctl restart bind9.service")
sleep(.5)

# Selesai
os.system("clear")
print("---KONFIGURAS DNS SERVER SELESAI---")
print("""----------***************-----------
Untuk pengujian, banyak caranya bisa ketik salah satu ini diterminal
1. dig hidhz.dev (nama domain)
2. nslookup
3. ping hidhz.dev (nama domain)
""")
print("----------***************-----------")
print("by @fs")
