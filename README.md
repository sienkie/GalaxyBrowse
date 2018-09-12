# GalaxyBrowse
A package of integrated Galaxy tools for genomic data visualization in JBrowse


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