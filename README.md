> **DEPRECATED:** This repository is deprecated. Please use https://github.com/goldenhelix/sentieon-secondary-analysis/ going forward. This README and the repository is retained for reference only.

# Sentieon Long Reads

This repository contains workflows for long-read genomic analysis using Sentieon's genomics tools. For detailed information about Sentieon's tools and algorithms, please refer to the [Sentieon Manual](https://support.sentieon.com/manual/).

## Prerequisite

Run the **Download Genomic Reference Resources** task to download and prepare the required local reference sequence and model files. These resources must be available on your system before running any of the workflows.

Before downloading, use [Workspace Settings](./manage/settings) to confirm the target location with the `RESOURCE_PATH` variable.

## Overview

This repository focuses exclusively on long-read analysis workflows and includes:

1. Germline analysis workflow that combines alignment and variant calling for PacBio long reads
2. Support for both HiFi and Oxford Nanopore Technologies (ONT) sequencing platforms

## Germline Analysis

### Germline Alignment and Variant Calling Workflow

The `sentieon_long_read_cli.workflow.yaml` file defines a workflow that performs two sequential steps:

1. **Alignment with Minimap2**: Aligns uBAM (unaligned BAM) files to a reference genome using Sentieon's implementation of Minimap2
2. **Variant Calling with Sentieon CLI**: Calls variants from the aligned BAM files using Sentieon's long-read optimized algorithms

This workflow is designed to process long-read samples from a directory structure where uBAM files follow the pattern `*_*.bam`. The sample name is extracted from the filename up to the first undersore (`_`).

#### Workflow Parameters

- **Input File Base Directory**: Directory containing uBAM files for processing
- **Output Folder**: Directory where results will be stored
- **Sequencing Technology**: Platform used for sequencing (HiFi or ONT)
- **Reference File**: FASTA file for alignment and variant calling; defaults to variables `${RESOURCES_PATH}/${REFERENCE_PATH}` set in the workspace settings
- **Sentieon Models Base Path**: Optional path to Sentieon model bundles for platform-specific optimization

### Minimap2 Alignment Task

The `sentieon_minimap2.task.yaml` file defines a task that performs alignment using Sentieon's implementation of Minimap2.

#### Key Features

- Supports uBAM (unaligned BAM) input files from long-read sequencers
- Optimized for both HiFi and ONT sequencing technologies
- Configurable machine learning models for platform-specific optimization
- Generates aligned BAM files ready for variant calling
- Automatic sample name extraction from input filenames

#### Task Parameters

- **Input Alignment File**: uBAM file from long-read sequencing
- **Sample Name**: Optional identifier for the sample (auto-extracted if not provided)
- **Output Folder**: Directory for alignment results
- **Technology**: Sequencing platform (HiFi or ONT)
- **Reference File**: FASTA file for alignment (defaults to workspace reference if not provided)
- **Sentieon Models Base Path**: Optional platform-specific model directory

### Sentieon CLI Long-Read Variant Calling Task

The `sentieon_cli_long_read.task.yaml` file defines a task that performs comprehensive variant calling using Sentieon's long-read optimized algorithms.

#### Key Features

- High-accuracy variant calling optimized for long-read data
- Support for both HiFi and ONT sequencing technologies
- Comprehensive variant detection including small variants and structural variants
- Optional gVCF output for joint genotyping workflows
- Integrated quality control with mosdepth
- Support for region-specific analysis with BED files
- Haploid region calling capabilities

#### Task Parameters

- **BAM Input**: Aligned BAM file from Minimap2 alignment
- **Sequencing Technology**: Platform used for sequencing (HiFi or ONT)
- **Sample Name**: Optional identifier for the sample
- **Output Folder**: Directory for variant calling results
- **Reference File**: FASTA file for variant calling (defaults to workspace default if not provided)
- **Region BED File**: Optional BED file to limit variant calling to specific regions
- **Haploid Regions BED**: Optional BED file specifying haploid regions for specialized calling
- **Advanced Options**:
  - Generate gVCF
  - Skip Small Variants
  - Skip SVs (Structural Variants)
  - Skip Mosdepth QC
  - Dry Run mode

## Input Requirements

### File Format
- **Input**: uBAM (unaligned BAM) files from long-read sequencers
- **Naming Convention**: Files should follow the pattern `*_*.bam` where the sample name is extracted from the filename up to the first `_`
- **Technology Support**: Compatible with both PacBio HiFi and Oxford Nanopore Technologies (ONT) data

### Data Quality
- For optimal results, ensure high-quality long-read data
- HiFi reads typically provide higher accuracy for variant calling
- ONT reads offer longer read lengths but may require different quality thresholds

## Output Files

The workflow generates several output files for each sample:

1. **Aligned BAM**: `{sample_name}_minimap2.bam` - Aligned reads ready for variant calling
2. **VCF**: `{sample_name}.vcf` - Called variants in standard VCF format
3. **gVCF**: `{sample_name}.g.vcf` - Genomic VCF format for joint genotyping (if enabled)
4. **QC Reports**: Various quality control metrics and reports
5. **Structural Variants**: SV calls in VCF format (if enabled)

