# login_brute_forcer
I wrote this to help brute force logins for the OSCP lab.  Currently supports what you see, I will add to it as I need.

#### TODO:
- Add all the protocols: telnet, smb, rdp, etc
- Make it faster....and faster...and faster
- Refine the output to get rid of uuid per result

# Example

cat /tmp/rhosts  
1.1.1.1  
1.1.1.2  
1.1.1.3  

cat /tmp/credentials  
john mypassword123  
fred hispassword123  
root toor  
  
python3 brutus.py --rhosts=rhosts --credentials=credentials --service=ssh  
