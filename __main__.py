import pulumi
import pulumi_yandex as yandex
from cloud_api import Image, YandexApi

## For more see:
# https://www.pulumi.com/registry/packages/yandex/api-docs/computeinstance/

## For run use:
# pulumi up -s dev -y

api = YandexApi()
ubuntu = Image(api).find_image('ubuntu-20').filds()

ISOImage = ubuntu.id
SSH_KEY = 'ssh-keys\\id_rsa.pub'
METADATA = 'metadata_instances\\vm_user_metadata'


class Network:
    def __init__(self, name='network1', ip_area='192.168.0.0/24'):
        self.name = name
        self.zone = 'ru-central1-a'
        self.v4_cidr_blocks = [ip_area]

    def create(self):
        self.network = yandex.VpcNetwork(self.name)
        # Create a new subnet in the network
        self.subnet = yandex.VpcSubnet(f'subnet-{self.name}',
                                       network_id=self.network.id,
                                       zone=self.zone,
                                       v4_cidr_blocks=self.v4_cidr_blocks,
                                       )

    def create_dns(self, name='zone1', zone_name='test-public-zone.ru.', public=True):
        # Field must match the pattern /[.]|[a-z0-9][-a-z0-9.]*\./
        self.zone = yandex.DnsZone(name,
                              description="DNS Zone Description",
                              labels={
                                  'label1': 'label-1-value',
                              },
                              zone=zone_name,
                              public=public,
                              private_networks=[self.network.id],
                              )
        return self.zone
    @staticmethod
    def print_dns(zone_id):
        dns = yandex.get_dns_zone(dns_zone_id=zone_id)
        pulumi.export("id", dns.id)
        pulumi.export("zone", dns.zone)


class Instance:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    # Note: API don't recive the "_" character!
    def __init__(self, vm_name, subnet):
        self.ZONE = "ru-central1-a"
        self.PLATFORM_ID = "standard-v1"
        self.hostname = vm_name
        self.name = vm_name
        self.resource_name = vm_name
        self.subnet = subnet
        # self.resource_name = 'resource-vm1'
        # self.name = 'name-vm1'


    def create(self, cores, memory):
        self.vm_instance = yandex.ComputeInstance(
            resource_name=self.resource_name,
            name=self.name,
            hostname=self.hostname,
            zone=self.ZONE,
            platform_id=self.PLATFORM_ID,
            allow_stopping_for_update=True,

            boot_disk=yandex.ComputeInstanceBootDiskArgs(
                auto_delete=True,
                initialize_params=yandex.ComputeInstanceBootDiskInitializeParamsArgs(
                    image_id=ISOImage,
                ),
            ),

            metadata={
                'ssh-keys': f'{open(SSH_KEY).read()}',
                'user-data': f'{open(METADATA).read()}',
            },

            network_interfaces=[
                yandex.ComputeInstanceNetworkInterfaceArgs(
                    nat=True,
                    ipv4=True,
                    ipv6=False,
                    subnet_id=self.subnet.id,
                    # nat_dns_records =
                    # dns_records = DnsRecordSet,
                )
            ],

            # allowed core number: 2, 4, 6, 8, 10, 12, 14, 16, 20, 24, 28, 32
            #  allowed core fractions: 5, 20, 100
            resources=yandex.ComputeInstanceResourcesArgs(
                cores=cores,
                memory=memory,
                core_fraction=5,
            ),
        )
        return self.vm_instance

    def create_dns_record(self, dns_record, dns_zone):
        yandex.DnsRecordSet(dns_record,
                            name=self.hostname,
                            zone_id=dns_zone.id,
                            type="A",
                            ttl=200,
                            datas=[self.vm_instance.network_interfaces[0]['nat_ip_address']],
                            )

    # For output
    @staticmethod
    def print_vm_info(vm_instance):
        pulumi.export('instanceName', vm_instance.name)
        pulumi.export('instanceHostname', vm_instance.hostname)
        pulumi.export('instanceId', vm_instance.id)
        pulumi.export('instanceFQDN', vm_instance.fqdn)
        pulumi.export('instanceCreated', vm_instance.created_at)
        pulumi.export('instanceMetadata', vm_instance.metadata)
        # pulumi.export('instanceNetworkInterfaces', vm_instance.network_interfaces)
        pulumi.export('instanceNatIp', vm_instance.network_interfaces[0]['nat_ip_address'])


def create_test_vms(num_machines, network):
    for index in range(1, num_machines + 1):
        vm_name = 'test-vm' + str(index)
        instance = Instance(vm_name, network.subnet)
        vm_instance = instance.create(cores=2, memory=2)
        dns_record = vm_name
        # instance.create_dns_record(dns_record, dns_zone)


num_machines = 2
network = Network()
network.create()
dns_zone = network.create_dns()
network.print_dns(dns_zone.id)
create_test_vms(num_machines, network)

# print(dir(vm_instance))
# print(dir(pulumi))

# default = yandex.ComputeDisk("default",
#     image_id="ubuntu-20-04-lts-v20230515",
#     labels={
#         "environment": "Pulumi-test",
#     },
#     type="network-ssd",
#     zone="ru-central1-a"
# )

# disk_id = 'fd83gfh90hpp3sojs1r3'
# disk_info = yandex.get_compute_disk(disk_id)
# print(disk_info)
