'''
I found a fairly elegant solution that works well for inline forms.

Applied to my model, where I'm filtering the inside_room field to only return rooms that are in the same building:
'''
#spaces/admin.py
class RoomInlineForm(ModelForm):
  def __init__(self, *args, **kwargs):
    super(RoomInlineForm, self).__init__(*args, **kwargs)  #On init...
  if 'instance' in kwargs:
        building = kwargs['instance'].building
  else:
        building_id = tuple(i[0] for i in self.fields['building'].widget.choices)[1]
        building = Building.objects.get(id=building_id)
  self.fields['inside_room'].queryset = Room.objects.filter(building__exact=building)
'''
Basically, if an 'instance' keyword is passed to the form, it's an existing record showing in the inline, and so I can just grab the building from the instance. If not an instance, it's one of the blank "extra" rows in the inline, and so it goes through the hidden form fields of the inline that store the implicit relation back to the main page, and grabs the id value from that. Then, it grabs the building object based on that building_id. Finally, now having the building, we can set the queryset of the drop downs to only display the relevant items.

More elegant than my original solution, which crashed and burned as inline (but worked--well, if you don't mind saving the form partway to make the drop downs fill in-- for the individual forms):
'''
class RoomForm(forms.ModelForm): # For the individual rooms
  class Meta:
mode = Room
  def __init__(self, *args, **kwargs):  # Limits inside_room choices to same building only
    super(RoomForm, self).__init__(*args, **kwargs)  #On init...
try:
  self.fields['inside_room'].queryset = Room.objects.filter( 
        building__exact=self.instance.building)   # rooms with the same building as this room
    except:                                      #and hide this field (why can't I exclude?)
        self.fields['inside_room']=forms.CharField( #Add room throws DoesNotExist error
                widget=forms.HiddenInput,       
                required=False,
                label='Inside Room (save room first)')
'''
For non-inlines, it worked if the room already existed. If not, it would throw an error (DoesNotExist), so I'd catch it and then hide the field (since there was no way, from the Admin, to limit it to the right building, since the whole room record was new, and no building was yet set!)...once you hit save, it saves the building and on reload it could limit the choices...

I just need to find a way to cascade the foreign key filters from one field to another in a new record--i.e., new record, select a building, and it automatically limits the choices in the inside_room select box--before the record gets saved. But that's for another day...
'''
