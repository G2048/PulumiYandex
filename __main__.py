import pulumi
import pulumi_yandex as yandex

## For more see:
# https://www.pulumi.com/registry/packages/yandex/api-docs/computeinstance/

# Ubuntu 20
ISOImage = 'fd808e721rc1vt7jkd0o'

network = yandex.VpcNetwork('network1')
# Create a new subnet in the network
subnet = yandex.VpcSubnet('subnet',
    network_id = network.id,
    zone = 'ru-central1-a',
    v4_cidr_blocks = ['192.168.0.0/24'],
)

# Field must match the pattern /[.]|[a-z0-9][-a-z0-9.]*\./
zone1 = yandex.DnsZone('zone1',
    description="DNS Zone Description",
    labels = {
        'label1': 'label-1-value',
    },
    zone = 'test-public-zone.ru.',
    public = True,
    private_networks = [network.id],
)


# Note: API don't recive the "_" character!
vm_instance = yandex.ComputeInstance(
    resource_name = 'resource-vm1',
    name = 'name-vm1',
    hostname = 'company-1',
    zone = "ru-central1-a",
    platform_id = "standard-v1",

    boot_disk = yandex.ComputeInstanceBootDiskArgs(
        auto_delete = True,
        initialize_params = yandex.ComputeInstanceBootDiskInitializeParamsArgs(
            image_id = ISOImage,
        ),
    ),

    metadata = {
        'ssh-keys': '{}'.format(open('ssh-keys\\id_rsa.pub').read()),
        'user-data': '{}'.format(open('metadata_instances\\vm_user_metadata').read()),
    },

    network_interfaces = [
        yandex.ComputeInstanceNetworkInterfaceArgs(
            nat = True,
            ipv4 = True,
            ipv6 = False,
            subnet_id = subnet.id,
            # dns_records = DnsRecordSet,
        )
    ],

    resources = yandex.ComputeInstanceResourcesArgs(
        cores = 2,
        memory = 4,
    ),
)

yandex.DnsRecordSet('rs1',
    name = 'test-vm1',
    zone_id = zone1.id,
    type = "A",
    ttl = 200,
    datas = [vm_instance.network_interfaces[0]['nat_ip_address']]
)


# For output
pulumi.export('instanceName', vm_instance.name)
pulumi.export('instanceHostname', vm_instance.hostname)
pulumi.export('instanceId', vm_instance.id)
pulumi.export('instanceFQDN', vm_instance.fqdn)
pulumi.export('instanceCreated', vm_instance.created_at)
pulumi.export('instanceMetadata', vm_instance.metadata)
pulumi.export('instanceNetworkInterfaces', vm_instance.network_interfaces)
pulumi.export('instanceNatIp', vm_instance.network_interfaces[0]['nat_ip_address'])
print(dir(vm_instance))

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