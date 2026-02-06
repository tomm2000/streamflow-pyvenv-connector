cwlVersion: v1.2
class: Workflow

requirements:
  MultipleInputFeatureRequirement: {}
  InlineJavascriptRequirement: {}
  StepInputExpressionRequirement: {}
  ScatterFeatureRequirement: {}

inputs: 
  in_element:
    type: string


outputs: 
  out_element:
    type: string
    outputSource: step3/out_element


steps:
# ============== Launch Server ==============
  step1:
    run: step1.cwl
    in:
      in_element: in_element
    out: [ out_element ]


  step2_1:
    run: step2.cwl
    in:
      in_element: step1/out_element
    out: [ out_element ]

  step2_2:
    run: step2.cwl
    in:
      in_element: step1/out_element
    out: [ out_element ]

  step2_3:
    run: step2.cwl
    in:
      in_element: step1/out_element
    out: [ out_element ]


  step3:
    run: step3.cwl
    in:
      in_elements: [  step2_1/out_element ,   step2_2/out_element ,   step2_3/out_element   ]
    out: [ out_element ]