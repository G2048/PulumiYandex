import pulumi
import pulumi_yandex as yandex
from cloud_managment.cloud_api import YandexApi
from cloud_managment.cloud_info import InfoImage

## For more see:
# https://www.pulumi.com/registry/packages/yandex/api-docs/computeinstance/

## For run use:
# pulumi up -s dev -y

api = YandexApi()
ubuntu = InfoImage(api).find_image('ubuntu-20').filds()

ISOImage = ubuntu.id
SSH_KEY = 'ssh-keys\\id_rsa.pub'
USER_METADATA = 'metadata_instances\\vm_user_metadata'


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

    # Something wrong with the DNS zone_name .... But I can't found another beautiful way
    def create_dns(self, name='zone1', zone_name='test-public-zone.ru.', public=True):
        # Field must match the pattern /[.]|[a-z0-9][-a-z0-9.]*\./
        self.dns_zone = yandex.DnsZone(name,
                                   description="DNS Zone Description",
                                   labels={
                                       'label1': 'label-1-value',
                                   },
                                   zone=zone_name,
                                   public=public,
                                   private_networks=[self.network.id],
                                   )
        return self.dns_zone

    @staticmethod
    def print_dns(dns_zone):
        #     zone         : "test-public-zone.ru."
        #     zone name    : "zone1-22e2d85"
        # dns = yandex.get_dns_zone(dns_zone_id=zone_id)
        pulumi.export("id", dns_zone.id)
        pulumi.export("zone", dns_zone.zone)
        pulumi.export("zone name", dns_zone.name)


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
        self.METADATA = {}
        # self.resource_name = 'resource-vm1'
        # self.name = 'name-vm1'

    def fill_metadata_instances(self, ssh_key: str, vm_metadata: str, dns_zone: str = ''):
        self.METADATA = {
            'ssh-keys': f'{open(ssh_key).read()}',
            'user-data': f'{open(vm_metadata).read()}',
            'dns_name': f'{self.name}.{str(dns_zone)}',
        }

    def create(self, cores: int, memory: int, *, core_fraction: int = 5):
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

            # "metadata_dns_name": "${local.dns_name}.${data.yandex_dns_zone.dns_zone_company-164907.zone}"
            metadata=self.METADATA,

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
                core_fraction=core_fraction,
            ),
        )
        return self.vm_instance

    def create_dns_record(self, dns_record, dns_zone_id):
        yandex.DnsRecordSet(dns_record,
                            name=dns_record,
                            # name=record_name,
                            zone_id=dns_zone_id,
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
    dns_zone_name = str(network.dns_zone.zone)
    # test-vm2.Calling __str__ on an Output[T] is not supported.
    #
    # To get the value of an Output[T] as an Output[str] consider:
    # 1. o.apply(lambda v: f"prefix{v}suffix")
    #
    # See https://www.pulumi.com/docs/concepts/inputs-outputs for more details.
    # This function may throw in a future version of Pulumi.
    pulumi.export('dns_zone_name', dns_zone_name)
    for index in range(1, num_machines + 1):
        vm_name = 'test-vm' + str(index)
        instance = Instance(vm_name, network.subnet)
        instance.fill_metadata_instances(ssh_key=SSH_KEY, vm_metadata=USER_METADATA, dns_zone=dns_zone_name)
        vm_instance = instance.create(cores=2, memory=2)
        dns_record = vm_name  # + '.'
        instance.create_dns_record(dns_record, dns_zone.id)


num_machines = 2
network = Network()
network.create()
dns_zone = network.create_dns()
create_test_vms(num_machines, network)
network.print_dns(dns_zone)

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
