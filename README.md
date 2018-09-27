# GalaxyBrowse

GalaxyBrowse is a package of integrated Galaxy tools for genomic data visualization in JBrowse Genome Browser. The main purpose of the tools is the automatization of data flow between a reproducible analysis of high-throughput genomic data and visualization which supports data sharing.
The main advantage of the package is providing an ability to visualize data directly from the Galaxy platform while avoiding unneeded file duplications.

#### Set-up

Before using GalaxyBrowse make sure JBrowse Genome Browser is installed on the web server and the reference genome has been formatted. Information about setting up JBrowse instance is available [here](http://jbrowse.org/code/JBrowse-1.12.1/docs/tutorial). If Galaxy and JBrowse are installed on different servers, the connection between them will need to be established. Furthermore, file systems should support the creation of symbolic links, which are requirements for both Galaxy and GalaxyBrowse package. Because of this, we recommend using SSHFS (Secure Shell File System) and checking appropriate access permissions, so that Galaxy can edit JBrowse files and create new directories.


#### Installation

Currently package isn't available in the Galaxy Tool Shed. To install tools on individual instances of the Galaxy platform perform following steps:

* clone repository into your Galaxy tools/ directory:

~~~
git clone https://github.com/sienkie/GalaxyBrowse.git
~~~

* copy lines below into your tool configuration file *tool_conf.xml* file located in the config/ directory of the Galaxy installation

~~~
<section id='galaxybrowse' name="GalaxyBrowse">
    <tool file="GalaxyBrowse/wrappers/jbrowse_prepare.xml" />
    <tool file="GalaxyBrowse/wrappers/jbrowse_add.xml" />
    <tool file="GalaxyBrowse/wrappers/jbrowse_remove.xml" />
</section>
~~~

For more information about configuring custom tools please refer to [this](https://galaxyproject.org/admin/tools/add-tool-tutorial/#4) tutorial.

#### GalaxyBrowse tools

To make managing data files in the genome browser easier, GalaxyBrowse functionality has been separated into three tools, which are described below.

##### JBrowse Prepare

This tool prepares sets of files that are located in the user history to be uploaded into the JBrowse genome browser. Supported file types include BED, BIGWIG, and VCF. JBrowse Prepare creates JSON file for every run, which contains information about datasets and configuration options for visualization. If no configuration options are specified, default options are used.

##### JBrowse Add

After creating one or multiple JSON files with JBrowse Prepare tool, JBrowse Add allows the user to visualize files according to configuration options specified in each file.  This tool will create a 'files' directory in JBrowse Genome Browser, creates symbolic links (unless otherwise specified) for data files according to input JSON files and use them to upload data to genome browser.

##### JBrowse Remove

This tool allows the user to remove data visualizations from genome browser based on tracks names or JSON files used to upload them.

