
================
Blender Notes
================



Rendering on the NIH Biowulf Cluster
=======================================

=========================================
:fa:`vr-cardboard` NIF Virtual Reality
=========================================



Running Blender render jobs on Biowulf
=========================================


.. figure:: ../_images/Guides/BlenderREndering/SubmitBlenderSwarm.png
  :align: right
  :width: 100%
  :figwidth: 30%

Rendering many frames of animation is computationally intensive and may take a long time even on a high end GPU. For faster rendering, Blender render jobs can be run on the `NIH High Performance Computing <https://hpc.nih.gov/>`_ cluster. 

Biowulf currently runs `Blender version 4.3.1 <https://www.blender.org/download/>`_ as a `Singularity <https://sylabs.io/docs/>`_ container, and can be run on either GPU (CUDA) or CPU, as noted in the `Biowulf documentation <https://hpc.nih.gov/apps/blender.html>`_. It is therefore recommended that you test your .blend file in a local copy of Blender 4.3 before copying the file to Helix:

- The easiest way to ensure paths to external assets (e.g. texture maps) are maintained is to select **File > External Data > Automatically Pack Into .blend**. This will increase the file size of the .blend file but will avoid the need to separately transfer external data and prevent paths from breaking.

- Update your render settings in the Render panel of the Properties editor, including resolution, paying particular attention to the 'Output' section. If you plan to run multiple jobs in parallel then you should tick the 'Placeholders' checkbox and untick the 'Overwrite' checkbox. This will create placeholder files once a render for the frame begins, so that the next process knows to continue to the next frame, and frames will not be overwritten.

- The file path and file formats specified in the .blend file's Output section will be overridden by the output path specified in the swarm file.

- Make a note of the frame range in the .blend file. You can specify a frame range to render in the swarm file, or you can set it to zero in order to use the frame range specified in the .blend file.


Once you have checked your .blend file and transferred it to Helix, log into Biowulf on NoMachine and open a Terminal window and type the following lines to start an interactive Matlab session:

.. code-block::

	sinteractive --mem=64g --cpus-per-task=8 --gres=gpu:p100:1
	module load matlab
	matlab


Blender doesn't run smoothly with virtual graphics cards, even when running background (GUI-less) rendering. Next, we therefore create a 'fake' display (X11) window, by typing the following commands in the terminal:

.. code-block::

	Xvfb -shmem -screen 0 1280x1024x24 &
	export DISPLAY=":0"
	module load blender CUDA/12.1

Next, in Matlab, open the `SubmitBlenderSwarm.m <>`_ GUI, and enter the parameters.




Blender command line arguments are outlined in the `Blender documentation <https://docs.blender.org/manual/en/latest/advanced/command_line/arguments.html>`_. 




Biowulf Visualization Partition 
----------------------------------

The Biowulf visualization partition is composed of K20x GPU nodes.  In contrast with other system resources, these nodes are allocated in their entirety to one user at a time.  Walltime limits are kept low since these resources are limited. To use the GPU hardware within the compute node, you will need to use TurboVNC and follow the procedure at `https://hpc.nih.gov/docs/svis.html <https://hpc.nih.gov/docs/svis.html>`_.









Camera Paths
===============


1) In the `3D viewport`, set a birds eye view of the scene ('View' > 'Viewpoint' > 'Top'). Then add a Bezier curve ('Add' > 'Curve' > 'Bezier')

2) In the `Properties` panel, select the `Data` tab, and check the box for `Path Animation`. Set the `Evaluation Time` parameter.

3) Select the camera, and in the `Properties` panel, select the `Constraints` tab. Add a `Follow Path` object constraint, with the Bezier curve path as the target, check `Follow curve` and set the forward and up axes as appropriate (usually forward = Y and up = Z).



Render passes
================

1) Object Index pass: in the `Properties` panel, select the `View Layer` tab. Under 'Passes' > 'Data' > 'Indexes' > check the 'Object Index' box. This will add an output to the Render Layers node called 'IndexOB'. The index value for each object in the scene can be set from the `Properties` panel 'Object' tab, under 'Relations' > 'Pass Index'.



