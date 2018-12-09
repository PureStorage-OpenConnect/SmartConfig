# SmartConfig Tool
Installation and User Guide

### Contents
+ ##### [Introduction](#Introduction)
    * ###### [FlashStack™ Deployment tool](#FlashStack-Deployment-tool)

+ ##### [Installation](#Installation)
    * ###### [System Requirements and Pre-Installation](#System-Requirements-and-Pre-Installation)
    * ###### [Tool Support Matrix](#Tool-Support-Matrix)
    * ###### [Hardware and software prerequisite](#Hardware-and-software-prerequisite)
    * ###### [Installing SmartConfig in host Environment](#Installing-SmartConfig-in-host-Environment)
    
+ ##### [Deploying FlashStack™](#Deploying-FlashStack)
+ ##### [Step 1. Select FlashStack Deployment Type](#Select-FlashStack-Deployment-Type)
+ ##### [Step 2. Enable DHCP for device discovery](#Enable-DHCP-for-device-discovery)
+ ##### [Step 3. Add FlashArray](#Add-FlashArray)
+ ##### [Step 4. Uploading the ISO libraries](#Uploading-the-ISO-libraries)
+ ##### [Step 5. Configuring FlashStack components](#Configuring-FlashStack-components)
+ ##### [Step 6. Device Initialization](#Device-Initialization)
+ ##### [Step 7. Workflow deployment](#Workflow-deployment)
+ ##### [SmartConfig Additional configurations](#SmartConfig-Additional-configurations)
+ ##### [Download Configuration](#Download-Configuration)
+ ##### [System logs](#System-logs)
+ ##### [Factory Reset](#Factory-Reset)
+ ##### [Troubleshooting SmartConfig](#Troubleshooting-SmartConfig)
+ ##### [Common Icons](#Common-Icons)
+ ##### [FAQ](#FAQ)


<a name="Introduction"></a>
## Introduction
SmartConfig is a provisioning tool to handle the basic zero-day deployment scenario for the FlashStack™ hardware

The tool covers the following aspects:

<a name="FlashStack-Deployment-tool"></a>
## FlashStack™ Deployment tool 

* Deployment tool for Pure FlashStack™ converged infrastructure solution
* Provides operational simplicity with GUI for Day-0 provisioning
* Provides the tool as a virtual appliance that can be hosted as VM in Oracle Virtual Box environment
* Tool to cover the following operations:
    * Automation of UCS basic and advanced workflows 
    * Workflows for MDS and Nexus switches
    * Provide VMware vSphere 6.5 hypervisor environment based on Cisco customized ISO image 
    * DHCP based Discovery
    * Integration with Pure Flash Array

This guide describes the steps for configuring FlashStack™ hardware using SmartConfig tool. In addition, it highlights best practices, illustrates configurations, and describes current limitations of the tool. The guide assumes that the FlashStack™ converged infrastructure is setup with the components physically connected as per CISCO validated Design (CVD) and the zero-day provisioning will be configured by the SmartConfig. 

<a name="Installation"></a>
## Installation
<a name="System-Requirements-and-Pre-Installation"></a>
### System Requirements and Pre-Installation:
Minimum requirement for hosting the SmartConfig Virtual Machine(VM) is as follows:
* SmartConfig VM has a fixed RAM size of 2GB, and it is recommended that customer does not change default RAM or storage settings
* The VM uses Cent OS (64 bit) as the base OS and occupies 3-4 GB of actual disk space, it can grow to 60 GB based on number of ISO uploaded

The optimal Host requirements are as follows:
* Windows/Linux/MAC with 4 GB ram, 64-bit processor and >= 3.2 GHz with Oracle virtual machine / VMware workstation installed
* VM requires to be deployed in an isolated network with accessibility to the flash stack for device auto discovery 
* No DHCP server should be running in the environment for device auto discovery

Network diagram for the configuration:

![alt text](./static/images/network-diagram.png)

<a name="Tool-Support-Matrix"></a>
### Tool Support Matrix
Pure Converged Infrastructure majorly supports the following deployment scenarios.

**(FA – Pure Flash Array, FI - Cisco Fabric Interconnect)**

| Sl.No | Components | +MDS  |  +Nexus 5k  |  +Nexus 9K |  Remarks
| :-----: | :-------: | :-----: |  :-----: | :-----: |  :----- |
| 1     | FA & FI | ![alt text](./static/images/success.png) |  | ![alt text](./static/images/success.png) | FC Config | 
| 2     | FA & FI | ![alt text](./static/images/success.png) | ![alt text](./static/images/success.png) | ![alt text](./static/images/m_xicon-1.png) | FC Config | 
| 3     | FA & FI | ![alt text](./static/images/success.png) |  | ![alt text](./static/images/m_xicon-1.png) | FC Config | 
| 4     | FA & FI | ![alt text](./static/images/m_xicon-1.png) | ![alt text](./static/images/success.png) | ![alt text](./static/images/m_xicon-1.png) | FC Config | 
| 5     | FA & FI | ![alt text](./static/images/m_xicon-1.png) | ![alt text](./static/images/m_xicon-1.png) | ![alt text](./static/images/m_xicon-1.png) | FC Direct Connect | 
| 6     | FA & FI | ![alt text](./static/images/m_xicon-1.png) | ![alt text](./static/images/m_xicon-1.png) | ![alt text](./static/images/success.png) | iSCSI Config | 
| 7     | FA & FI | ![alt text](./static/images/m_xicon-1.png) | ![alt text](./static/images/success.png) | ![alt text](./static/images/m_xicon-1.png) | iSCSI Config | 
| 8     | FA & FI |  |  |  | iSCSI Direct Connect | 

The current SmartConfig Tool (version 1.1) only supports following deployment scenarios
* FA//MDS//Nexus 9k//FI (FC)
* FA//Nexus 9K//FI (iSCSI)

<a name="Hardware-and-software-prerequisite"></a>
### Hardware and software prerequisite 
Following are the minimum hardware and software requirements 

| Layer | Hardware | Version |
| :-----: | :-------: | :-----: |
| **Compute** | UCS (FI)   | **3.1(3a)** |
| **Storage** | MDS        | **7.3**     |
| **Network** | Nexus 9k   | **6.x**     |
| **Storage** | FlashArray | **4.9.3**   |

<a name="Installing-SmartConfig-in-host-Environment"></a>
### Installing SmartConfig in host Environment
##### Step 1. Launch SmartConfig OVA using Oracle Virtual box/VMware workstation
Once launched, SmartConfig VM console screen displays the IP information for the tool.  User will be able to alter the IP settings by selecting the advanced option in VM console.

![VM Console](./static/images/vm-console1.png "VM Console") ![VM Console](./static/images/vm-console2.png "VM Console")
![VM Console](./static/images/vm-console3.png "VM Console") ![VM Console](./static/images/vm-console4.png "VM Console")

Launch the IP(http://<ip>/) in web browser for accessing SmartConfig tool as shown in below screen.

![EULA Agreement](./static/images/eula-agreement.png "EULA Agreement")

##### Step 2. Review and Accept EULA Agreement
Accept EULA Agreement to start using the tool

![EULA Agreement](./static/images/eula-agreement1.png "EULA Agreement")

User will be able to use the tool, only after the EULA is accepted.
<a name="Deploying-FlashStack"></a>
### Deploying FlashStack™
<a name="Select-FlashStack-Deployment-Type"></a>
#### Step 1. Select FlashStack Deployment Type 
The FlashStack deployment screen is used to select the FlashStack type for deployment.

![Deployment Type Selection](./static/images/stack-selection.png "Deployment Type Selection")

<a name="Enable-DHCP-for-device-discovery"></a>
#### Step 2. Enable DHCP for device discovery
By default, DHCP discovery is disabled in the tool. User needs to enable it to discover available FlashStack™ hardware in the network
Below screen shows no devices discovered
![Discovery](./static/images/discovery-empty.png "Discovery")

Below screen shows DHCP settings.

![DHCP Settings](./static/images/dhcp-settings.png "DHCP Settings")

**Note:**  ‘DHCP range’ will be used to provide IP for hardware during discovery phase and ‘STATIC range’ will be used to auto suggest IP during Initial Configuration. 

Below Screen shows discovered FlashStack Hardware once the DHCP has been enabled:

![Discovery](./static/images/discovery.png "Discovery")

**Note:** Based on the flash stack selection you have made, user need to select the correct number of hardware to move to the next step. The colour indicator in the Devices tittle bar turns green when right number of hardware is selected.
Please note that some hardware may require a reboot to get it discovered.

<a name="Add-FlashArray"></a>
#### Step 3. Add Flash Array 
Current version of SmartConfig does not support auto discovery of FlashArray and it needs to be added ![Burger/Menu Icon](./static/images/burger-icon.png "Burger/Menu Icon") manually by clicking burger icon     > Add FlashArray. Provide credentials for FlashArray when prompted. 

![Add FlashArray](./static/images/add-flasharray.png "Add FlashArray")

<a name="Uploading-the-ISO-libraries"></a>
#### Step 4. Uploading the ISO libraries
SmartConfig requires the user to upload the images/kickstart file for various FlashStack components. The uploaded firmware images will be used during initial flashing of hardware and during ESX installation in blade server.

![ISO Library](./static/images/iso-library.png "ISO Library")

Please refer to FlashStack™ documentation to identify appropriate images and upload to the tool.

<a name="Configuring-FlashStack-components"></a>
#### Step 5. Configuring FlashStack components
Select required number of unconfigured devices for the flash stack selection you made as per CVD and click on next for initial configuration options.

Enter the component name, IP address, Gateway, netmask and other respective details (NEXUS/MDS and select firmware images that have been uploaded to the ISO library in previous step) as shown in screens below.

![Basic Configuration](./static/images/configuration.png "Basic Configuration")

Switch to advanced tab for configuration for advanced user

![Advanced Configuration](./static/images/advanced-configuration.png "Advanced Configuration")

<a name="Device-Initialization"></a>
#### Step 6. Device Initialization
Click on initialize button to flush the configurations to the respective hardware as shown in the below screen

![Device Initialization](./static/images/device-initialization.png "Device Initialization")

Screen shot below shows configuration update in progress

![Device Initialization](./static/images/device-initialization-status.png "Device Initialization")

<a name="Workflow-deployment"></a>
#### Step 7. Workflow deployment
SmartConfig offers two methods of deployment
* Basic / Single Touch deployment 
* Advanced deployment

**Basic/Single Touch Deployment:**
In Basic deployment, the user will be provided with a single touch deployment, where standard inputs defined as per CISCO validated design (CVD) will be used for deployment. The tool will take care of the Deployment once the user clicks on “Deploy” button. During the deployment, tool provides status of the deployment.

**Advanced deployment:**
Advanced workflow deployment is meant for user who wants to edit the field values prior to deployment to certain specific values as per their needs. It consists of sub workflows and each sub workflow containing individual tasks. Each task will have its own input and needs to be configured prior to the deployment of the same.

Below screen shot shows the basic deployment in progress.

![Advanced Deployment](./static/images/basic-deployment.png "Advanced Deployment")

Below screen shot shows advanced workflow deployment

![Advanced Deployment Finished state](./static/images/basic-deployment-finished.png "Advanced Deployment Finished state")

Below is the screen shot for advanced workflow configuration group


![Advanced Deployment Group](./static/images/basic-deployment-inprogress.png "Advanced Deployment Group")

Below is the screen shot for advanced workflow inputs

![Task Input](./static/images/task-inputs.png "Task Input")

<a name="SmartConfig-Additional-configurations"></a>
### SmartConfig Additional configurations
<a name="Download-Configuration"></a>
#### Download Configuration

SmartConfig allows the user to download the configurations used for deployment once deployment is complete. The option will be available next to finish button

<a name="System-logs"></a>
#### System logs

SmartConfig users can download system log by going to About > System logs. The log can be used to diagnose any system defects by support team. 

<a name="Factory-Reset"></a>
#### Factory Reset

Factory reset will bring the VM back to the original factory settings, all logs will be deleted. 

Note: Factory reset will not clear contents of ISO library

Below is the screen shot for system logs and factory reset icons in help page

![Factory Reset](./static/images/about-us.png "Factory Reset")

<a name="Troubleshooting-SmartConfig"></a>
### Troubleshooting SmartConfig
1. Unable to discover the device
    * Ensure the device is properly connected to management network
    * Reboot the device
      
2. Failure during initial configuration of flash stack components
    * Perform a reboot/factory reset physically
      
3. Failure during Workflow deployment
    * Ensure the task parameters values are intact in case of advanced workflow
    * Finish the deployment and perform factory reset of the hardware and restart the initial configuration and deployment.


<a name="Common-Icons"></a>
### Common Icons

The Following table provides information about the common icons used in the End User Portal. You can see the name of an icon when you hover over it with your mouse. Some icons may have a different name, depending upon the context in which they’re used.

| Icon | Name | Description |
| :-----: | :------- | :----- |
| <i class="fa fas fa-sync faa-spin animated blue-text"></i> | In-Progress | The icon represents **in-progress state** for operations in SmartConfig |
| ![Burger Menu](./static/images/burger-icon.png "Burger Menu") | Menu | This icon represents any **additional options**. |
| <div class="icon">![Reachable/Online](./static/images/online.png "Reachable/Online")</div> | Reachable(Online) | The icon is used to represent **Online state** of a device |
| <div class="icon">![Reachable/Offline](./static/images/offline.png "Reachable/Offline")</div> | Not Reachable(Offline) | The icon is used to represent **Offline state** of a device |
| <i class="fa fas fa-times"></i> | Close | To represent closure of a window or popup. |
| <i class="fa fas fa-trash-alt red-text"></i> | Trash | Click **Trash** to delete an object, such as devices, images, etc |
| <i class="fa fas fa-th-large"></i> | Library | This icon is used for **uploading and selecting** the firmware images. |
| <i class="fa fas fa-info-circle"></i> | Info | To represent detailed information |
| <i class="fa fas fa-question-circle"></i> | Help | Represents generic help. |
| <span class="required"></span> | Asterisks | Indiactes mandatory field to be filled. |
| <div class="progress-bar orange-bar shine stripes small"><span class="orange-background" style="width: 50%"></span></div> | Progress bar | Shows the progress of an operation |
| <i class="fa fas fa-expand-arrows-alt"></i> | Expand | This icon appears in each block of the flow. Where the user can click and see **expanded view** of the block. |
| <i class="fa fas fa-download"></i> | Download | Represents the **download** operation. |
| <i class="fa fas fa-plus-circle"></i> | Zoom In | Represents the **zoom in/scale up** operation. |
| <i class="fa fas fa-minus-circle"></i> | Zoom Out | Represents the **zoom out/scale down** operation. |
| <i class="fa fas fa-stop-circle"></i> | Zoom Reset | To reset the zoom operation. |
| <i class="fa fas fa-clipboard-list"></i> | System Log | To **download** the syetem log |
| <i class="fa fas fa-undo red-text"></i> | Factory Reset | This icon is used to **Reset** the tool |
| <i class="fa fas fa-check-circle green-text"></i> | Success | Represents the **successful completion** of an operation. |
| <i class="fa fas fa-exclamation-triangle red-text"></i> | Warning | Represents the **failed state** of an operation. |
| <i class="fa fas fa-play blue-text"></i> | Play | To **Trigger** an operation |
| <i class="fa fas fa-pencil-alt"></i> | Edit | Represents to **edit/modify** the default value of an object. |
| <i class="fa fas fa-clipboard-list grey-text"></i> | Log | Shows the deployment log for each workflow. Error logs shows the exact CLI failures. |
| <div class="icon">![Rolling Back](./static/images/anticlockwise.gif "Rolling Back")</div> | Rolling Back | The icon represents **Rolling Back state** for operations in SmartConfig |


<a name="FAQ"></a>
### FAQ

1. Why DHCP is required?

    > DHCP is used for discovering the FlashStack hardware components available in the network. Only devices in factory reset state will be discovered via DHCP. DHCP is also used to update the firmware for MDS and Nexus using POAP.

2. What the slider DHCP & Static Range in DHCP settings used for?

    > DHCP range is used to provide IP for devices in the network for discovery purpose. Static range is used to provide IP suggestion for hardware during initial configuration.

3. How to add FlashArray?

    > Go to burger icon ![Burger/Menu Icon](./static/images/burger-icon.png "Burger/Menu Icon") in discovery page and select add FlashArray. Provide credentials when prompted.

4. Why FlashArray is not getting discovered?

    > Current SmartConfig has no auto discovery mechanism for FlashArray. Flash array needs to be added manually

5. How to use custom VLAN ID, VSAN ID, port-channel settings?

    > VLAN, VSAN, port-channel settings can be modified in configuration step > advanced tab.

6. How to factory reset the tool?

    > Got to About us, click on ‘Factory Reset’. Factory reset will remove all the configurations. Please note that the factory reset will not remove contents of ISO library

7. How to download diagnostic logs?

    > Go to About us, click on ‘System Logs’ to start downloading the log.

8. What is ISO library?

    > ISO library is used to store the firmware update images for MDS, NEXUS and ESX iso.

9. How to upload kickstart for ISO?

    > ESX kickstart file can be added by going to ISO library, select type as ESXi kickstart, and select the ESX iso from drop down, select file and upload

10. How to download the deployment configuration?

    > Deployment configuration can be downloaded after a successful deployment 

11. Can I upgrade an already existing FlashStack?

    > No, currently SmartConfig can be only used for a Day-0 Deployment scenario

12. What does discovery do?

    > Discovery stage allows automatic discovery of hardware components, selection for initial configuration. User needs to select the hardware which are required for the flash stack selection he has made. 

13. What is the deployment stage?

    > Deployment stage runs multiple workflows to configure the hardware.


