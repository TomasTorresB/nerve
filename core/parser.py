import socket
import datetime

from socket import gethostname
from core.utils import Network, Utils
from flask_babel import _

class SchemaParser:
  def __init__(self, data, req):
    self.data = data
    self.utils = Utils()
    self.netutils = Network()
    self.metadata = {
      'unique_id' : self.utils.generate_uuid(),
      'timestamp' : self.utils.get_datetime(),
      'node': gethostname(),
      'issuer':{
        'user_agent':req.headers.get('User-Agent'),
        'source_ip':req.remote_addr
        }
      }
    self.data['metadata'] = self.metadata
    
  def verify(self):
    verified = True
    error = None
  
    try:
      # Targets
      networks = self.data['targets']['networks']
      excluded_networks = self.data['targets']['excluded_networks']
      domains = self.data['targets']['domains']
      
      # Scan Definition
      name = self.data['config']['name']
      description = self.data['config']['description']
      engineer = self.data['config']['engineer']
      webhook = self.data['config']['post_event']['webhook']
      intrusive_level = self.data['config']['allow_aggressive']
      allow_dos = self.data['config']['allow_dos']
      allow_bf = self.data['config']['allow_bf']
      allow_inet = self.data['config']['allow_internet']
      dictionary_usernames = self.data['config']['dictionary']['usernames']
      dictionary_passwords = self.data['config']['dictionary']['passwords']
      max_ports = self.data['config']['scan_opts']['max_ports']
      custom_ports = self.data['config']['scan_opts']['custom_ports']
      net_interface  = self.data['config']['scan_opts']['interface']
      parallel_scan   = self.data['config']['scan_opts']['parallel_scan']
      parallel_attack = self.data['config']['scan_opts']['parallel_attack']
      frequency = self.data['config']['frequency']
      schedule_date = self.data['config']['schedule_date']
      
      """
        Check Structure
      """
      if not isinstance(name, str):
        error = _('Option [ASSESSMENT_NAME] must be a String')
        verified = False
      
      if not isinstance(networks, list):
        error = _('Option [NETWORKS] must be an Array')
        verified = False
      
      if not isinstance(excluded_networks, list):
        error = _('Option [EXCLUDED_NETWORKS] must be an Array')
        verified = False
      
      if not isinstance(domains, list):
        error = _('Option [DOMAINS] must be an Array')
        verified = False

      if not isinstance(intrusive_level, int):
        error = _('Option [AGGRESSIVENESS_LEVEL] must be an Integer')
        verified = False
      
      if not isinstance(allow_dos, bool):
        error = _('Option [ALLOW_DENIAL_OF_SERVICE] must be a Boolean')
        verified = False
      
      if not isinstance(allow_inet, bool):
        error = _('Option [ALLOW_INTERNET_OUTBOUND] must be a Boolean')
        verified = False
      
      if not isinstance(allow_bf, bool):
        error = _('Option [ALLOW_BRUTE_FORCE] must be a Boolean')
        verified = False
      
      if not isinstance(dictionary_usernames, list):
        error = _('Option [DICTIONARY_USERNAMES] must be an Array')
        verified = False
      
      if not isinstance(dictionary_passwords, list):
        error = _('Option [DICTIONARY_PASSWORDS] must be an Array')
        verified = False
      
      if not isinstance(net_interface, (str, type(None))):
        error = _('Option [NET_INTERFACE] must be null or a String')
        verified = False

      if not isinstance(max_ports, int):
        error = _('Option [MAX_PORTS] must be an Integer')
        verified = False
      
      if not isinstance(custom_ports, list):
        error = _('Option [MAX_PORTS] must be an Array')
        verified = False

      if not isinstance(custom_ports, list):
        error = _('Option [CUSTOM_PORTS] must be an Array')
        verified = False

      if not isinstance(parallel_scan, int):
        error = _('Option [PARALLEL_SCAN] must be an Integer')
        verified = False
      
      if not isinstance(parallel_attack, int):
        error = _('Option [PARALLEL_ATTACK] must be an Integer')
        verified = False
      
      if not isinstance(webhook, (str, type(None))):
        error = _('Option [WEB_HOOK] must be null or a String')
        verified = False

      if not isinstance(frequency, str):
        error = _('Option [FREQUENCY] must be a String')
        verified = False

      if not isinstance(schedule_date, str):
        error = _('Option [SCHEDULE_DATE] must be a String')
        verified = False

      if not verified:
        return (verified, error, self.data)
      
      """
        Check passed values
      """

      if len(name) > 30 or not self.utils.is_string_safe(name):
        error = _('Option [ASSESSMENT_NAME] must not exceed 30 characters and must not have special characters.')
        verified = False
      
      if description:
        if len(description) > 200 or not self.utils.is_string_safe(description):
          error = _('Option [ASSESSMENT_DESCRIPTION] must not exceed 200 characters and must not have special characters.')
          verified = False
      
      if engineer:
        if len(engineer) > 20 or not self.utils.is_string_safe(engineer):
          error = _('Option [ENGINEER] must not exceed 20 characters and must not have special characters.')
          verified = False
      
      if webhook:
        if not self.utils.is_string_url(webhook):
          error = _('Option [WEB_HOOK] must be a valid URL.')
          verified = False
      
      if frequency not in ('once', 'continuous','schedule'):
        error = _('Option [SCHEDULE] must be "once" or "continuous" or "schedule"')
        verified = False

      if not schedule_date and frequency == 'schedule':
        error = _('Option [SCHEDULE_DATE] must not be empty if scheduling a scan')
        verified = False

      if schedule_date:
        # split throws exception when delimiter is not present.
        # int throws exception when string value is not int. 
        # datetime throws exception when date is not valid.
        try: 
          date_time_split = schedule_date.split("T")
          date_part = date_time_split[0].split("-")
          time_part = date_time_split[1].split(":")
          yyyy = int(date_part[0])
          mm = int(date_part[1])
          dd = int(date_part[2])
          hh = int(time_part[0])
          mins = int(time_part[1])
   
          # Verify correct format
          check_date = datetime.datetime(year=yyyy,month=mm,day=dd,hour=hh,minute=mins)

          # Check scheduled date is posterior to current date
          if (datetime.datetime.now() > check_date): 
            error = _('Option [SCHEDULE_DATE] must not be prior to current date')
            verified = False
          # Verify date is no more than 2100
          if (yyyy > 2100):
            error = _('Option [SCHEDULE_DATE] must not surpass year 2100')
            verified = False
        except Exception as e:
           error = _('Option [SCHEDULE_DATE] must be in date format yyyy-mm-ddThh:mm')
           verified = False

      if not 0 <= intrusive_level <= 3:
        error = _('Option [AGGRESSIVE_LEVEL] must be between 0-3')
        verified = False
          
      if max_ports:
        if not self.netutils.is_valid_port(max_ports):
          error = _('Option [MAX_PORTS] must be a value between 0-65535')
          verified = False          

      if custom_ports:
        for cport in custom_ports:
          if not self.netutils.is_valid_port(cport):
            error = _('Option [CUSTOM_PORTS] must be an array of values between 0-65535')
            verified = False
        
      if not networks and not domains:
        error = _('Options [DOMAINS] or Options [NETWORKS] must not be empty')
        verified = False
        
      if networks:
        for network in networks:
          try:
            if not self.netutils.is_network(network): 
              error = _('Option [NETWORKS] must be a valid network CIDR')
              raise ValueError
            elif self.netutils.is_network_in_denylist(network):
              error = _('Option [NETWORKS] is not allowed')   
              raise ValueError
          
          except ValueError:
            verified = False
        
      if excluded_networks:
        for network in excluded_networks:
          try:
            if not self.netutils.is_network(network):
              raise ValueError
          except ValueError:
            error = _('Option [EXCLUDED NETWORKS] must be a valid network CIDR')
            verified = False
      
      if domains:
        for domain in domains:
          if not self.netutils.is_dns(domain):
            error = _('Option [DOMAINS] must contain valid domains (and they must be resolveable!)')
            verified = False
      
      if net_interface:
        n = Network()
        if not net_interface in n.get_nics():
          error = _('Option [NET_INTERFACE] must be valid')
          verified = False
      
      else:
        self.data['config']['scan_opts']['interface'] = None
      
      if not 1 <= parallel_attack <= 100:
        error = _('Option [ATTACK_THREADS] must be between 1-100')
        verified = False

      if not 1 <= parallel_scan <= 100:
        error = _('Option [SCAN_THREADS] must be between 1-100')
        verified = False
   
    except KeyError as e:
      error = _('One or more options are missing: %(err)s', err=e)
      verified = False
      
    return (verified, error, self.data)
  
  def get_cfg(self):
    return self.data
  
class ScanParser:
  def __init__(self, port, values):
    self.port = port
    self.values = values

  def get_cpe(self):
    return self.values['port_data'][self.port]['cpe']

  def get_version(self):
    return self.values['port_data'][self.port]['version']

  def get_module(self):
    return self.values['port_data'][self.port]['module']

  def get_product(self):
    product = 'N/A'
    if self.values['port_data'][self.port]['product']:
      product = self.values['port_data'][self.port]['product']
    return product

  def get_portstate(self):
    return self.values['port_data'][self.port]['state']

  def get_ports(self):
    return self.values['ports']
  
  def get_domain(self):
    return self.values['domain']
  
class ConfParser:
  def __init__(self, cfg):
    self.values = cfg
  
  def get_raw_cfg(self):
    return self.values
  
  def get_cfg_metadata(self):
    return self.values['metadata']

  def get_cfg_scan_id(self):
    return self.values['metadata']['unique_id']
  
  def get_cfg_scan_config(self):
    return self.values['config']
  
  def get_cfg_scan_targets(self):
    return self.values['targets']
  
  def get_cfg_networks(self):
    return self.values['targets']['networks']

  def get_cfg_exc_networks(self):
    return self.values['targets']['excluded_networks']
  
  def get_cfg_domains(self):
    return self.values['targets']['domains']
  
  def get_cfg_aggressive_lvl(self):
    return self.values['config']['allow_aggressive']
  
  def get_cfg_allow_dos(self):
    return self.values['config']['allow_dos']
  
  def get_cfg_allow_inet(self):
    return self.values['config']['allow_internet']
    
  def get_cfg_allow_bf(self):
    return self.values['config']['allow_bf']
    
  def get_cfg_max_ports(self):
    return self.values['config']['scan_opts']['max_ports']
  
  def get_cfg_custom_ports(self):
    return self.values['config']['scan_opts']['custom_ports']
  
  def get_cfg_usernames(self):
    return self.values['config']['dictionary']['usernames']
  
  def get_cfg_passwords(self):
    return self.values['config']['dictionary']['passwords']
  
  def get_cfg_netinterface(self):
    return self.values['config']['scan_opts']['interface']
  
  def get_cfg_attack_threads(self):
    return self.values['config']['scan_opts']['parallel_attack']
  
  def get_cfg_scan_threads(self):
    return self.values['config']['scan_opts']['parallel_scan']

  def get_cfg_webhook(self):
    return self.values['config']['post_event']['webhook']
  
  def get_cfg_frequency(self):
    return self.values['config']['frequency']

  def get_cfg_schedule(self):
    return self.values['config']['schedule_date']
 
class Helper:
  def cpeHyperlink(self, cpe):
    return '<a href="https://nvd.nist.gov/vuln/search/results?cpe_version={0}">CVE List</a>'.format(cpe)

  def cveHyperlink(self, cve):
    return '<a href="https://nvd.nist.gov/vuln/detail/{0}">{0}</a>'.format(cve)
    
  def portTranslate(self, port):
    translation = 'Unknown'
    try:
      translation = socket.getservbyport(port)
    except OSError:
      pass   
    return translation

