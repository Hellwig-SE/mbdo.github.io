# Trafo Publications mini Tool
This tool provides the transformation of a publications file in the form of 
``` 
* [CJP+23] B. Combemale, J. Jézéquel, Q. Perez, D. Vojtisek, N. Jansen, J. Michael, F. Rademacher, B. Rumpe, A. Wortmann, J. Zhang:  
[Model-Based DevOps: Foundations and Challenges](https://www.se-rwth.de/publications/Model-Based-DevOps-Foundations-and-Challenges.pdf). In: Int. Conf. on Model Driven Engineering Languages and Systems Companion (MODELS-C), pp. 429–433, ACM/IEEE, Oct. 2023.
```

to a HTML like this:

``` 
<details name="pubs"> <summary>[CZA+26] <strong>A Software Architecture for Real-Time Digital Twins in Machining</strong> (2026) <br> <strong> Shengjian Chen, Jingxi Zhang, Samed Ajdinovi, Oliver Jud, Lars Klingel, Alexander Verl, Andreas Wortmann</strong> </summary> <img src="/assets/img/papers/paper1.png" alt="Preview of paper" style="max-width: 300px; height: auto; margin-top: 10px;"> <p><strong>Authors:</strong> Shengjian Chen, Jingxi Zhang, Samed Ajdinovi, Oliver Jud, Lars Klingel, Alexander Verl, Andreas Wortmann</p> <p><strong>Venue:</strong> 8th Workshop on Modeling and Simulation of Software-Intensive Systems</p> <p><strong>Abstract:</strong> Digital twins are increasingly recognized as a key enabler for optimizing complex systems by providing virtual representations that are continuously updated with real-world data. To unlock their full potential, real-time capabilities are essential, ensuring that decision-making, monitoring, and control can be performed with minimal latency. However, previous work has mainly concentrated on offline analysis or loosely coupled synchronization, leaving the systematic design of scalable and reliable real-time digital twins insufficiently addressed. In this paper we introduce a reference architecture for implementing real-time digital twins, covering requirements such as data acquisition, integration, synchronization, and processing, and highlighting enabling technologies that support low-latency and dependable operations. To validate this approach, we developed a prototype framework and applied it to a machine tool case study, demonstrating how real-time synchronization and decision support can be achieved in practice. The results show that our framework enables consistent, high-frequency interaction between physical and virtual assets, providing a foundation for advanced applications in monitoring, control, and optimization of manufacturing systems. </p> <p> <strong>Links:</strong> <a href="#"> http://camps.aptaracorp.com//ACM_PMS/PMS/ACM/MSSIS26/1/91846627-109f-11f1-aa9c-16ffd757ba29/OUT/mssis26-1.html </a> · <a href="#"> 10.1145/3786146.3788640 </a> </p> <button type="button" class="btn btn-sm btn-outline-secondary copy-cite" data-target="cite-paper-2"> Cite </button> <span class="copy-feedback" style="margin-left: 0.5rem; font-size: 0.9rem;"></span> <pre id="cite-paper-2" hidden>PRE</pre> </details>

```

Execute with
``` python trafo_publications.py source.md target/publications_generated.html ```

Generating the extras.json:
```python trafo_publications.py source.md target/publications_generated.html --write-extras-template extras.json```

Using the extras.json:
```python trafo_publications.py source.md target/publications_generated.html --extras extras.json --write-extras-template extras.json```