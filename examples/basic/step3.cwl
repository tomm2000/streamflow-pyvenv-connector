#!/usr/bin/env cwl-runner

cwlVersion: v1.2
class: CommandLineTool

baseCommand: ["/bin/sh", "-c"]

requirements:
  - class: InlineJavascriptRequirement

inputs: 
  in_elements:
    type: string[]

outputs: 
  out_element:
    type: string
    outputBinding:
      glob: stdout.txt
      loadContents: true
      outputEval: $(self[0].contents.trim())

stdout: stdout.txt

arguments:
  - valueFrom: "sleep 1; echo $(inputs.in_elements)"

  